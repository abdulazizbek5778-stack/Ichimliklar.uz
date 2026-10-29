/**
 * DOKONIFY — Core Logic, Stories (24/7 Permanent Archive), Google Auth, and Store State
 */

// Default store data with social features and 24/7 Stories Archive
const DEFAULT_STORE = {
  name: "Chashma Drinks",
  slug: "chashma-drinks",
  category: "drinks",
  icon: "🥤",
  phone: "+998 90 123-45-67",
  address: "Toshkent shahri, Chilonzor tumani",
  currency: "so'm",
  tgBot: "@chashma_drinks_bot",
  balance: 3840000,
  bannerText: "Yangi mavsum aksiyasi! Barcha salqin ichimliklarga 15% chegirma!",
  stories: [
    {
      id: 1,
      title: "🔥 Aksiya -15%",
      caption: "Barcha muzdek ichimliklarga 15% chegirma haftaligi boshlandi!",
      image: "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=600&q=80",
      avatar: "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=150&q=80",
      date: "Doimiy arxiv (24/7)"
    },
    {
      id: 2,
      title: "🥤 Yangi Moxito",
      caption: "Muzdek ohak va yalpiz ekstrakti bilan yangilangan tabiiy limonad!",
      image: "https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=600&q=80",
      avatar: "https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=150&q=80",
      date: "Doimiy arxiv (24/7)"
    },
    {
      id: 3,
      title: "🚚 Bepul Yetkazish",
      caption: "Toshkent bo'ylab 50,000 so'mdan yuqori buyurtmalar 30 daqiqada yetkaziladi!",
      image: "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=600&q=80",
      avatar: "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=150&q=80",
      date: "Doimiy arxiv (24/7)"
    },
    {
      id: 4,
      title: "⭐ Sharhlar",
      caption: "Mijozlarimizdan kelgan iliq fikrlar va samimiy tavsiyalar!",
      image: "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=600&q=80",
      avatar: "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=150&q=80",
      date: "Doimiy arxiv (24/7)"
    }
  ],
  products: [
    {
      id: 7,
      name: "Borjomi Tabiiy Mineral Gazlangan Suv 0.5L",
      category: "water",
      price: 16000,
      oldPrice: 19000,
      image: "https://images.unsplash.com/photo-1559839914-1b311394b986?auto=format&fit=crop&w=400&q=80",
      description: "Gruziyaning tabiiy vulqon kelib chiqishiga ega mashhur mineral gazlangan suvi. 60 dan ortiq minerallarga boy. 0.5L shisha.",
      stock: 50,
      isPopular: true,
      likes: 118,
      comments: [
        { id: 1, author: "Akmal aka", text: "Borjomi har doim original va muzdek keladi, rahmat!", time: "Bugun, 14:00" },
        { id: 2, author: "Zilola", text: "Oshqozon og'rig'ida eng zo'r yordamchi suv.", time: "Kechagi kunda" }
      ]
    },
    {
      id: 8,
      name: "Tog‘ Chashmasi Toza Gazsiz Suv (Bezgaz) 1.0L",
      category: "water",
      price: 5000,
      oldPrice: 7000,
      image: "https://images.unsplash.com/photo-1548839140-29a749e1bc4e?auto=format&fit=crop&w=400&q=80",
      description: "Tabiiy tog‘ buloqlaridan olingan toza, yumshoq va salqin gazsiz (bezgaz) tabiiy ichimlik suvi. 1.0L.",
      stock: 50,
      isPopular: true,
      likes: 94,
      comments: [
        { id: 1, author: "Davron", text: "Juda toza va ta'mi shirin gazsiz suv, har kuni olamiz!", time: "2 soat oldin" }
      ]
    },
      id: 1,
      name: "Tog' Chashmasi Mineral Suv 1.5L",
      category: "drinks",
      price: 6000,
      oldPrice: 8000,
      image: "https://images.unsplash.com/photo-1548839140-29a749e1bc4e?auto=format&fit=crop&w=400&q=80",
      description: "Tabiiy tog' buloqlaridan olingan toza, gazsiz mineral ichimlik suvi.",
      stock: 45,
      isPopular: true,
      likes: 42,
      comments: [
        { id: 1, author: "Sardor", text: "Suv juda toza va shirin ekan, doim olamiz!", time: "2 soat oldin" },
        { id: 2, author: "Madina", text: "Muzdek holda yetkazib berishdi, rahmat!", time: "Kechagi kunda" }
      ]
    },
    {
      id: 2,
      name: "Moxito Fresh (Limon & Yalpiz) 0.5L",
      category: "drinks",
      price: 18000,
      oldPrice: 22000,
      image: "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=400&q=80",
      description: "Muzdek tabiiy ohak va yalpiz ekstraktli serob gazlangan limonad.",
      stock: 28,
      isPopular: true,
      likes: 89,
      comments: [
        { id: 1, author: "Javohir", text: "Yozgi issiqda eng zo'r ichimlik! Tavsiya qilaman 🔥", time: "Bugun, 15:30" }
      ]
    },
    {
      id: 3,
      name: "Tabiiy Anor Sharbati 1L",
      category: "drinks",
      price: 24000,
      oldPrice: 28000,
      image: "https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?auto=format&fit=crop&w=400&q=80",
      description: "100% tabiiy siqilgan quyuq anor sharbati, shakarsiz.",
      stock: 35,
      isPopular: false,
      likes: 56,
      comments: [
        { id: 1, author: "Olim aka", text: "Haqiqiy tabiiy anor suvi, bolalarga ham foydali.", time: "3 kun oldin" }
      ]
    },
    {
      id: 4,
      name: "Muzli Qahva (Iced Latte Caramel)",
      category: "drinks",
      price: 22000,
      oldPrice: null,
      image: "https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?auto=format&fit=crop&w=400&q=80",
      description: "Arabika qahva donalari, yangi sut va karamel siropi bilan tayyorlangan salqin qahva.",
      stock: 19,
      isPopular: true,
      likes: 74,
      comments: [
        { id: 1, author: "Nozima", text: "Karameli juda yoqdi, yana zakaz beraman!", time: "Bugun, 18:00" }
      ]
    },
    {
      id: 5,
      name: "Apelsin Fresh Organik 0.4L",
      category: "drinks",
      price: 20000,
      oldPrice: 25000,
      image: "https://images.unsplash.com/photo-1613478223719-2ab802602423?auto=format&fit=crop&w=400&q=80",
      description: "Yangi uzilgan apelsinlardan siqilgan vitaminlarga boy sharbat.",
      stock: 15,
      isPopular: false,
      likes: 31,
      comments: []
    },
    {
      id: 6,
      name: "Klassik Muzdek Limonad 1L",
      category: "drinks",
      price: 15000,
      oldPrice: null,
      image: "https://images.unsplash.com/photo-1523371067-1793740e6988?auto=format&fit=crop&w=400&q=80",
      description: "Uy sharoitida tayyorlanganidek nozik limon va sitrus ifori.",
      stock: 50,
      isPopular: true,
      likes: 63,
      comments: [
        { id: 1, author: "Bobur", text: "Narxi ham juda yaxshi, yetkazib berish ham tez.", time: "1 kun oldin" }
      ]
    }
  ],
  orders: [
    {
      id: "ORD-9421",
      customer: "Sardor Alimov",
      phone: "+998 90 777-11-22",
      address: "Yunusobod 4-mavze, 12-uy",
      items: "Moxito Fresh (2 dona), Tog' Chashmasi (4 dona)",
      total: 60000,
      payment: "Click",
      status: "Yangi",
      date: "Bugun, 21:15"
    },
    {
      id: "ORD-9420",
      customer: "Dilnoza Karimova",
      phone: "+998 93 456-78-90",
      address: "Mirzo Ulug'bek, Mustaqillik shoh ko'chasi 54",
      items: "Tabiiy Anor Sharbati (2 dona)",
      total: 48000,
      payment: "Payme",
      status: "Yetkazilmoqda",
      date: "Bugun, 20:40"
    }
  ]
};

// State Accessors
function getStore() {
  const data = localStorage.getItem('dokonify_store');
  if (!data) {
    localStorage.setItem('dokonify_store', JSON.stringify(DEFAULT_STORE));
    return DEFAULT_STORE;
  }
  const store = JSON.parse(data);
  // Ensure stories exists and is array (24/7 permanent archive)
  if (!Array.isArray(store.stories)) {
    store.stories = DEFAULT_STORE.stories;
  }
  // Ensure products have likes & comments structure
  if (store.products) {
    store.products.forEach(p => {
      if (typeof p.likes !== 'number') p.likes = Math.floor(10 + Math.random() * 50);
      if (!Array.isArray(p.comments)) p.comments = [];
    });
  }
  return store;
}

function saveStore(store) {
  localStorage.setItem('dokonify_store', JSON.stringify(store));
}

function getCart() {
  return JSON.parse(localStorage.getItem('dokonify_cart') || '[]');
}

function saveCart(cart) {
  localStorage.setItem('dokonify_cart', JSON.stringify(cart));
}

// CSRF cookie helper for Django POST requests
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return '';
}

function getLikedItems() {
  return JSON.parse(localStorage.getItem('dokonify_liked_items') || '[]');
}

function saveLikedItems(liked) {
  localStorage.setItem('dokonify_liked_items', JSON.stringify(liked));
}

// Google Auth State
function getGoogleUser() {
  const data = localStorage.getItem('dokonify_google_user');
  return data ? JSON.parse(data) : null;
}

function saveGoogleUser(user) {
  if (user) {
    localStorage.setItem('dokonify_google_user', JSON.stringify(user));
  } else {
    localStorage.removeItem('dokonify_google_user');
  }
}

// Format numbers in Uzbek Sum
function formatSum(num) {
  return new Intl.NumberFormat('uz-UZ').format(num) + " so'm";
}

// Slug generator
function slugify(text) {
  return text.toString().toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w\-]+/g, '')
    .replace(/\-\-+/g, '-');
}

// Like functionality
function toggleProductLike(productId) {
  const store = getStore();
  const product = store.products.find(p => p.id === productId);
  if (!product) return;

  let liked = getLikedItems();
  const isLiked = liked.includes(productId);

  if (isLiked) {
    liked = liked.filter(id => id !== productId);
    product.likes = Math.max(0, (product.likes || 1) - 1);
  } else {
    liked.push(productId);
    product.likes = (product.likes || 0) + 1;
  }

  saveLikedItems(liked);
  saveStore(store);

  if (typeof renderProducts === 'function') {
    renderProducts();
  }
}

// Comment functionality
function addProductComment(productId, author, text) {
  if (!text || !text.trim()) return false;
  const store = getStore();
  const product = store.products.find(p => p.id === productId);
  if (!product) return false;

  if (!Array.isArray(product.comments)) {
    product.comments = [];
  }

  const newComment = {
    id: Date.now(),
    author: author.trim() || "Mijoz",
    text: text.trim(),
    time: "Hozirgina"
  };

  product.comments.unshift(newComment);
  saveStore(store);

  if (typeof renderProducts === 'function') {
    renderProducts();
  }
  return true;
}
