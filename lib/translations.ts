export type Language = 'zh-CN' | 'zh-TW' | 'ja' | 'en';

interface Translations {
  hero: {
    title: string;
    titleAccent: string;
    subtitle: string;
  };
  categories: {
    browseByCategory: string;
    all: string;
    fiction: string;
    nonFiction: string;
    mystery: string;
    scienceFiction: string;
    biography: string;
  };
  books: {
    allBooks: string;
    book: string;
    books: string;
    available: string;
    awardWinner: string;
    noBooks: string;
  };
  footer: {
    curatedCollection: string;
  };
}

export const translations: Record<Language, Translations> = {
  'zh-CN': {
    hero: {
      title: '获奖图书',
      titleAccent: '文学收藏',
      subtitle: '探索不同类型的著名作品，从普利策奖获奖者到现代畅销书'
    },
    categories: {
      browseByCategory: '按类别浏览',
      all: '全部',
      fiction: '小说',
      nonFiction: '非小说',
      mystery: '悬疑',
      scienceFiction: '科幻',
      biography: '传记'
    },
    books: {
      allBooks: '全部图书',
      book: '本书',
      books: '本书',
      available: '可用',
      awardWinner: '获奖作品',
      noBooks: '此类别中未找到图书'
    },
    footer: {
      curatedCollection: '精选获奖文学作品集'
    }
  },
  'zh-TW': {
    hero: {
      title: '獲獎圖書',
      titleAccent: '文學收藏',
      subtitle: '探索不同類型的著名作品，從普立茲獎獲獎者到現代暢銷書'
    },
    categories: {
      browseByCategory: '按類別瀏覽',
      all: '全部',
      fiction: '小說',
      nonFiction: '非小說',
      mystery: '懸疑',
      scienceFiction: '科幻',
      biography: '傳記'
    },
    books: {
      allBooks: '全部圖書',
      book: '本書',
      books: '本書',
      available: '可用',
      awardWinner: '獲獎作品',
      noBooks: '此類別中未找到圖書'
    },
    footer: {
      curatedCollection: '精選獲獎文學作品集'
    }
  },
  'ja': {
    hero: {
      title: '受賞作品',
      titleAccent: '文学コレクション',
      subtitle: 'ピューリッツァー賞受賞作から現代のベストセラーまで、様々なジャンルの名作を発見'
    },
    categories: {
      browseByCategory: 'カテゴリー別に閲覧',
      all: 'すべて',
      fiction: '小説',
      nonFiction: 'ノンフィクション',
      mystery: 'ミステリー',
      scienceFiction: 'SF',
      biography: '伝記'
    },
    books: {
      allBooks: 'すべての本',
      book: '冊',
      books: '冊',
      available: '利用可能',
      awardWinner: '受賞作品',
      noBooks: 'このカテゴリーに本が見つかりません'
    },
    footer: {
      curatedCollection: '厳選された受賞文学作品コレクション'
    }
  },
  'en': {
    hero: {
      title: 'Award-Winning',
      titleAccent: 'Literary Collection',
      subtitle: 'Discover celebrated works across genres, from Pulitzer Prize winners to modern bestsellers'
    },
    categories: {
      browseByCategory: 'Browse by Category',
      all: 'All',
      fiction: 'Fiction',
      nonFiction: 'Non-Fiction',
      mystery: 'Mystery',
      scienceFiction: 'Science Fiction',
      biography: 'Biography'
    },
    books: {
      allBooks: 'All Books',
      book: 'book',
      books: 'books',
      available: 'available',
      awardWinner: 'Award Winner',
      noBooks: 'No books found in this category'
    },
    footer: {
      curatedCollection: 'Curated collection of award-winning literature'
    }
  }
};

export const languageNames: Record<Language, string> = {
  'zh-CN': '简体中文',
  'zh-TW': '繁體中文',
  'ja': '日本語',
  'en': 'English'
};
