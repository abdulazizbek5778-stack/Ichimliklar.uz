from django.contrib.auth.models import User
from django.test import Client, TestCase

from .models import Order, Product, StoreConfig, Story


class AdminPasskeyTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='store-admin',
            password='strong-test-password',
            is_staff=True,
        )

    def test_dashboard_redirects_when_not_logged_in(self):
        response = self.client.get('/dashboard/')

        self.assertRedirects(response, '/owner/login/')

    def test_dashboard_is_available_to_staff(self):
        self.client.force_login(self.admin)

        response = self.client.get('/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Face ID bilan kirish')

    def test_passkey_options_require_staff(self):
        response = self.client.post('/api/auth/passkey/register/begin/')

        self.assertEqual(response.status_code, 403)

    def test_staff_can_start_passkey_registration(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            '/api/auth/passkey/register/begin/',
            HTTP_HOST='localhost',
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        options = response.json()
        self.assertIn('challenge', options)
        self.assertEqual(options['authenticatorSelection']['authenticatorAttachment'], 'platform')
        self.assertTrue(self.client.session.get('webauthn_register_challenge'))

    def test_passkey_login_requires_a_registered_credential(self):
        response = self.client.post(
            '/api/auth/passkey/login/begin/',
            HTTP_HOST='localhost',
            secure=True,
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('Passkey hali sozlanmagan', response.json()['message'])

    def test_only_staff_can_use_admin_mutation_apis(self):
        response = self.client.post('/api/product/create/', data='{}', content_type='application/json')

        self.assertEqual(response.status_code, 403)

    def test_login_page_has_no_default_password(self):
        response = self.client.get('/owner/login/')

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'value="1234"')
        self.assertNotContains(response, 'value="xurramov_abdulaziz"')

    def test_password_login_keeps_a_working_fallback(self):
        response = self.client.post(
            '/api/auth/login/',
            data='{"username":"store-admin","password":"strong-test-password"}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['redirect'], '/dashboard/')
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_password_login_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.get('/owner/login/')

        response = csrf_client.post(
            '/api/auth/login/',
            data='{"username":"store-admin","password":"strong-test-password"}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)

    def test_password_login_can_register_passkey_with_rotated_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.get('/owner/login/')
        csrf_token = csrf_client.cookies['csrftoken'].value
        login_response = csrf_client.post(
            '/api/auth/login/',
            data='{"username":"store-admin","password":"strong-test-password"}',
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(login_response.status_code, 200)
        fresh_csrf_token = csrf_client.cookies['csrftoken'].value
        response = csrf_client.post(
            '/api/auth/passkey/register/begin/',
            data='{}',
            content_type='application/json',
            HTTP_HOST='localhost',
            HTTP_X_CSRFTOKEN=fresh_csrf_token,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('challenge', response.json())

    def test_staff_can_create_update_and_delete_products(self):
        self.client.force_login(self.admin)
        payload = {
            'name': 'Limonad',
            'category': 'drinks',
            'price': '12000',
            'stock': 8,
            'image': 'https://example.com/drink.jpg',
            'description': 'Yangi ichimlik',
        }

        created = self.client.post('/api/product/create/', payload, content_type='application/json')
        self.assertEqual(created.status_code, 200)
        product_id = created.json()['product']['id']
        self.assertTrue(Product.objects.filter(pk=product_id, name='Limonad').exists())
        catalog = self.client.get('/api/store/catalog/')
        self.assertEqual(catalog.json()['products'][0]['name'], 'Limonad')

        updated = self.client.post(
            f'/api/product/update/{product_id}/',
            {**payload, 'name': 'Limonad tahrirlangan', 'price': '15000'},
            content_type='application/json',
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(Product.objects.get(pk=product_id).name, 'Limonad tahrirlangan')

        deleted = self.client.post(f'/api/product/delete/{product_id}/')
        self.assertEqual(deleted.status_code, 200)
        self.assertFalse(Product.objects.filter(pk=product_id).exists())

    def test_staff_can_create_and_delete_a_public_post(self):
        self.client.force_login(self.admin)
        created = self.client.post(
            '/api/story/create/',
            {'title': 'Yangi post', 'caption': 'Aksiya', 'image': 'https://example.com/post.jpg'},
            content_type='application/json',
        )

        self.assertEqual(created.status_code, 200)
        story_id = created.json()['story']['id']
        self.assertEqual(created.json()['story_id'], story_id)
        catalog = self.client.get('/api/store/catalog/')
        self.assertEqual(catalog.json()['stories'][0]['title'], 'Yangi post')

        deleted = self.client.post(f'/api/story/delete/{story_id}/', data='{}', content_type='application/json')
        self.assertEqual(deleted.status_code, 200)
        self.assertFalse(Story.objects.filter(pk=story_id).exists())

    def test_admin_dashboard_reads_persistent_orders_and_settings(self):
        self.client.force_login(self.admin)
        order = Order.objects.create(
            order_id='ORD-TEST',
            customer='Ali',
            phone='+998900000000',
            address='Toshkent',
            items='Limonad',
            total='12000',
        )
        response = self.client.get('/api/admin/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['orders'][0]['id'], order.order_id)
        self.assertEqual(response.json()['revenue'], '12000')
        self.assertEqual(response.json()['active_orders'], 1)

        saved = self.client.post(
            '/api/admin/settings/',
            {'name': 'Yangi do‘kon', 'phone': '+99890', 'banner_text': 'Aksiya', 'tg_bot': '@ichimliklar'},
            content_type='application/json',
        )
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(StoreConfig.objects.get().name, 'Yangi do‘kon')
