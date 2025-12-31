import { Language } from './translations';

export interface Book {
  id: string;
  title: Record<Language, string>;
  author: Record<Language, string>;
  category: string;
  award: Record<Language, string>;
  year: number;
  coverImage: string;
  description: Record<Language, string>;
}

export const categories = [
  "All",
  "Fiction",
  "Non-Fiction",
  "Mystery",
  "Science Fiction",
  "Biography"
];

export const books: Book[] = [
  // Fiction
  {
    id: "1",
    title: {
      'zh-CN': '午夜图书馆',
      'zh-TW': '午夜圖書館',
      'ja': 'ミッドナイト・ライブラリー',
      'en': 'The Midnight Library'
    },
    author: {
      'zh-CN': '马特·海格',
      'zh-TW': '麥特·海格',
      'ja': 'マット・ヘイグ',
      'en': 'Matt Haig'
    },
    category: "Fiction",
    award: {
      'zh-CN': 'Goodreads 读者选择奖',
      'zh-TW': 'Goodreads 讀者選擇獎',
      'ja': 'Goodreads Choice Award',
      'en': 'Goodreads Choice Award'
    },
    year: 2020,
    coverImage: "/images/books/midnight-library.jpg",
    description: {
      'zh-CN': '一部关于人生所有选择的精彩小说，探讨如何过好一生。',
      'zh-TW': '一部關於人生所有選擇的精彩小說，探討如何過好一生。',
      'ja': '人生のすべての選択についての魅力的な小説。',
      'en': 'A dazzling novel about all the choices that go into a life well lived.'
    }
  },
  {
    id: "2",
    title: {
      'zh-CN': '我们看不见的光',
      'zh-TW': '我們看不見的光',
      'ja': '私たちが見えないすべての光',
      'en': 'All the Light We Cannot See'
    },
    author: {
      'zh-CN': '安东尼·多尔',
      'zh-TW': '安東尼·多爾',
      'ja': 'アンソニー・ドーア',
      'en': 'Anthony Doerr'
    },
    category: "Fiction",
    award: {
      'zh-CN': '普利策奖',
      'zh-TW': '普立茲獎',
      'ja': 'ピューリッツァー賞',
      'en': 'Pulitzer Prize'
    },
    year: 2014,
    coverImage: "/images/books/all-the-light.jpg",
    description: {
      'zh-CN': '讲述一个盲人法国女孩和一个德国男孩在被占领的法国相遇的故事。',
      'zh-TW': '講述一個盲人法國女孩和一個德國男孩在被佔領的法國相遇的故事。',
      'ja': '占領下のフランスで出会った盲目のフランス人少女とドイツ人少年の物語。',
      'en': 'A novel about a blind French girl and a German boy whose paths collide in occupied France.'
    }
  },
  {
    id: "3",
    title: {
      'zh-CN': '树冠之上',
      'zh-TW': '樹冠之上',
      'ja': 'オーバーストーリー',
      'en': 'The Overstory'
    },
    author: {
      'zh-CN': '理查德·鲍尔斯',
      'zh-TW': '理查德·鮑爾斯',
      'ja': 'リチャード・パワーズ',
      'en': 'Richard Powers'
    },
    category: "Fiction",
    award: {
      'zh-CN': '普利策奖',
      'zh-TW': '普立茲獎',
      'ja': 'ピューリッツァー賞',
      'en': 'Pulitzer Prize'
    },
    year: 2018,
    coverImage: "/images/books/overstory.jpg",
    description: {
      'zh-CN': '一部难忘的小说，讲述九个陌生人因自然灾难而走到一起的故事。',
      'zh-TW': '一部難忘的小說，講述九個陌生人因自然災難而走到一起的故事。',
      'ja': '展開する自然災害によって結びつけられた9人の見知らぬ人々の忘れられない物語。',
      'en': 'An unforgettable novel about nine strangers brought together by an unfolding natural catastrophe.'
    }
  },
  {
    id: "4",
    title: {
      'zh-CN': '哈姆内特',
      'zh-TW': '哈姆内特',
      'ja': 'ハムネット',
      'en': 'Hamnet'
    },
    author: {
      'zh-CN': '玛吉·奥法雷尔',
      'zh-TW': '瑪吉·奧法雷爾',
      'ja': 'マギー・オファーレル',
      'en': 'Maggie O\'Farrell'
    },
    category: "Fiction",
    award: {
      'zh-CN': '女性小说奖',
      'zh-TW': '女性小說獎',
      'ja': '女性小説賞',
      'en': 'Women\'s Prize for Fiction'
    },
    year: 2020,
    coverImage: "/images/books/hamnet.jpg",
    description: {
      'zh-CN': '一幅婚姻的光辉画卷，一次家庭悲剧的震撼描绘。',
      'zh-TW': '一幅婚姻的光輝畫卷，一次家庭悲劇的震撼描繪。',
      'ja': '結婚生活の輝かしい肖像、家族の悲劇の衝撃的な描写。',
      'en': 'A luminous portrait of a marriage, a shattering evocation of a family tragedy.'
    }
  },
  
  // Non-Fiction
  {
    id: "5",
    title: {
      'zh-CN': '人类简史',
      'zh-TW': '人類簡史',
      'ja': 'サピエンス全史',
      'en': 'Sapiens'
    },
    author: {
      'zh-CN': '尤瓦尔·赫拉利',
      'zh-TW': '尤瓦爾·赫拉利',
      'ja': 'ユヴァル・ノア・ハラリ',
      'en': 'Yuval Noah Harari'
    },
    category: "Non-Fiction",
    award: {
      'zh-CN': '英国年度图书',
      'zh-TW': '英國年度圖書',
      'ja': 'イギリス年間最優秀図書',
      'en': 'British Book of the Year'
    },
    year: 2011,
    coverImage: "/images/books/sapiens.jpg",
    description: {
      'zh-CN': '从石器时代到现代的人类简史。',
      'zh-TW': '從石器時代到現代的人類簡史。',
      'ja': '石器時代から現代までの人類の簡潔な歴史。',
      'en': 'A brief history of humankind from the Stone Age to the modern age.'
    }
  },
  {
    id: "6",
    title: {
      'zh-CN': '你当像鸟飞往你的山',
      'zh-TW': '你當像鳥飛往你的山',
      'ja': '教育',
      'en': 'Educated'
    },
    author: {
      'zh-CN': '塔拉·韦斯特弗',
      'zh-TW': '塔拉·韋斯特弗',
      'ja': 'タラ・ウェストーバー',
      'en': 'Tara Westover'
    },
    category: "Non-Fiction",
    award: {
      'zh-CN': 'Goodreads 读者选择奖',
      'zh-TW': 'Goodreads 讀者選擇獎',
      'ja': 'Goodreads Choice Award',
      'en': 'Goodreads Choice Award'
    },
    year: 2018,
    coverImage: "/images/books/educated.jpg",
    description: {
      'zh-CN': '一位年轻女性离开生存主义家庭并获得博士学位的回忆录。',
      'zh-TW': '一位年輕女性離開生存主義家庭並獲得博士學位的回憶錄。',
      'ja': 'サバイバリストの家族を離れ、博士号を取得した若い女性の回顧録。',
      'en': 'A memoir about a young woman who leaves her survivalist family and goes on to earn a PhD.'
    }
  },
  {
    id: "7",
    title: {
      'zh-CN': '海拉细胞的不朽人生',
      'zh-TW': '海拉細胞的不朽人生',
      'ja': 'ヘンリエッタ・ラックスの不死の生',
      'en': 'The Immortal Life of Henrietta Lacks'
    },
    author: {
      'zh-CN': '丽贝卡·思克鲁特',
      'zh-TW': '麗貝卡·思克魯特',
      'ja': 'レベッカ・スクルート',
      'en': 'Rebecca Skloot'
    },
    category: "Non-Fiction",
    award: {
      'zh-CN': '美国国家科学院传播奖',
      'zh-TW': '美國國家科學院傳播獎',
      'ja': '全米科学アカデミーコミュニケーション賞',
      'en': 'National Academies Communication Award'
    },
    year: 2010,
    coverImage: "/images/books/henrietta-lacks.jpg",
    description: {
      'zh-CN': '海拉细胞和改变医学的永生细胞系的故事。',
      'zh-TW': '海拉細胞和改變醫學的永生細胞系的故事。',
      'ja': 'ヘンリエッタ・ラックスと医学を変えた不死の細胞系の物語。',
      'en': 'The story of Henrietta Lacks and the immortal cell line that changed medicine.'
    }
  },
  
  // Mystery
  {
    id: "8",
    title: {
      'zh-CN': '龙纹身的女孩',
      'zh-TW': '龍紋身的女孩',
      'ja': 'ドラゴン・タトゥーの女',
      'en': 'The Girl with the Dragon Tattoo'
    },
    author: {
      'zh-CN': '斯蒂格·拉森',
      'zh-TW': '斯蒂格·拉森',
      'ja': 'スティーグ・ラーソン',
      'en': 'Stieg Larsson'
    },
    category: "Mystery",
    award: {
      'zh-CN': '玻璃钥匙奖',
      'zh-TW': '玻璃鑰匙獎',
      'ja': 'グラス・キー賞',
      'en': 'Glass Key Award'
    },
    year: 2005,
    coverImage: "/images/books/dragon-tattoo.jpg",
    description: {
      'zh-CN': '一名记者和一名黑客调查一个四十年前的谜团。',
      'zh-TW': '一名記者和一名駭客調查一個四十年前的謎團。',
      'ja': 'ジャーナリストとハッカーが40年前の謎を調査する。',
      'en': 'A journalist and a hacker investigate a forty-year-old mystery.'
    }
  },
  {
    id: "9",
    title: {
      'zh-CN': '消失的爱人',
      'zh-TW': '消失的愛人',
      'ja': 'ゴーン・ガール',
      'en': 'Gone Girl'
    },
    author: {
      'zh-CN': '吉莉安·弗琳',
      'zh-TW': '吉莉安·弗琳',
      'ja': 'ギリアン・フリン',
      'en': 'Gillian Flynn'
    },
    category: "Mystery",
    award: {
      'zh-CN': 'Goodreads 读者选择奖',
      'zh-TW': 'Goodreads 讀者選擇獎',
      'ja': 'Goodreads Choice Award',
      'en': 'Goodreads Choice Award'
    },
    year: 2012,
    coverImage: "/images/books/gone-girl.jpg",
    description: {
      'zh-CN': '当妻子在结婚纪念日失踪时，一段婚姻的秘密被揭露。',
      'zh-TW': '當妻子在結婚紀念日失蹤時，一段婚姻的秘密被揭露。',
      'ja': '記念日に妻が失踪したとき、結婚生活の秘密が明らかになる。',
      'en': 'A marriage\'s secrets are exposed when a wife disappears on her anniversary.'
    }
  },
  {
    id: "10",
    title: {
      'zh-CN': '沉默的病人',
      'zh-TW': '沉默的病人',
      'ja': 'サイレント・ペイシェント',
      'en': 'The Silent Patient'
    },
    author: {
      'zh-CN': '亚历克斯·迈克利兹',
      'zh-TW': '亞歷克斯·邁克利茲',
      'ja': 'アレックス・マイケライズ',
      'en': 'Alex Michaelides'
    },
    category: "Mystery",
    award: {
      'zh-CN': 'Goodreads 读者选择奖',
      'zh-TW': 'Goodreads 讀者選擇獎',
      'ja': 'Goodreads Choice Award',
      'en': 'Goodreads Choice Award'
    },
    year: 2019,
    coverImage: "/images/books/silent-patient.jpg",
    description: {
      'zh-CN': '一名女性对丈夫实施暴力后拒绝开口说话。',
      'zh-TW': '一名女性對丈夫實施暴力後拒絕開口說話。',
      'ja': '夫に対する暴力行為の後、話すことを拒否する女性。',
      'en': 'A woman\'s act of violence against her husband and her refusal to speak thereafter.'
    }
  },
  
  // Science Fiction
  {
    id: "11",
    title: {
      'zh-CN': '三体',
      'zh-TW': '三體',
      'ja': '三体',
      'en': 'The Three-Body Problem'
    },
    author: {
      'zh-CN': '刘慈欣',
      'zh-TW': '劉慈欣',
      'ja': '劉慈欣',
      'en': 'Liu Cixin'
    },
    category: "Science Fiction",
    award: {
      'zh-CN': '雨果奖',
      'zh-TW': '雨果獎',
      'ja': 'ヒューゴー賞',
      'en': 'Hugo Award'
    },
    year: 2008,
    coverImage: "/images/books/three-body.jpg",
    description: {
      'zh-CN': '中国秘密军事计划向太空发送信号以与外星人建立联系。',
      'zh-TW': '中國秘密軍事計劃向太空發送信號以與外星人建立聯繫。',
      'ja': '中国の秘密軍事計画が宇宙に信号を送り、宇宙人との接触を確立する。',
      'en': 'China\'s secret military program sends signals into space to establish contact with aliens.'
    }
  },
  {
    id: "12",
    title: {
      'zh-CN': '挽救计划',
      'zh-TW': '挽救計劃',
      'ja': 'プロジェクト・ヘイル・メアリー',
      'en': 'Project Hail Mary'
    },
    author: {
      'zh-CN': '安迪·威尔',
      'zh-TW': '安迪·威爾',
      'ja': 'アンディ・ウィアー',
      'en': 'Andy Weir'
    },
    category: "Science Fiction",
    award: {
      'zh-CN': 'Goodreads 读者选择奖',
      'zh-TW': 'Goodreads 讀者選擇獎',
      'ja': 'Goodreads Choice Award',
      'en': 'Goodreads Choice Award'
    },
    year: 2021,
    coverImage: "/images/books/hail-mary.jpg",
    description: {
      'zh-CN': '一名孤独的宇航员必须在这部引人入胜的惊悚片中拯救地球。',
      'zh-TW': '一名孤獨的太空人必須在這部引人入勝的驚悚片中拯救地球。',
      'ja': '孤独な宇宙飛行士がこの魅力的なスリラーで地球を救わなければならない。',
      'en': 'A lone astronaut must save the earth from disaster in this irresistibly readable thriller.'
    }
  },
  {
    id: "13",
    title: {
      'zh-CN': '第五季',
      'zh-TW': '第五季',
      'ja': '第五の季節',
      'en': 'The Fifth Season'
    },
    author: {
      'zh-CN': 'N.K.杰米辛',
      'zh-TW': 'N.K.傑米辛',
      'ja': 'N.K.ジェミシン',
      'en': 'N.K. Jemisin'
    },
    category: "Science Fiction",
    award: {
      'zh-CN': '雨果奖',
      'zh-TW': '雨果獎',
      'ja': 'ヒューゴー賞',
      'en': 'Hugo Award'
    },
    year: 2015,
    coverImage: "/images/books/fifth-season.jpg",
    description: {
      'zh-CN': '一名女性在不断受到灾难威胁的世界中寻找她的女儿。',
      'zh-TW': '一名女性在不斷受到災難威脅的世界中尋找她的女兒。',
      'ja': '絶え間ない災害に脅かされる世界で娘を探す女性。',
      'en': 'A woman searches for her daughter in a world constantly threatened by catastrophe.'
    }
  },
  
  // Biography
  {
    id: "14",
    title: {
      'zh-CN': '史蒂夫·乔布斯传',
      'zh-TW': '史蒂夫·賈伯斯傳',
      'ja': 'スティーブ・ジョブズ',
      'en': 'Steve Jobs'
    },
    author: {
      'zh-CN': '沃尔特·艾萨克森',
      'zh-TW': '沃爾特·艾薩克森',
      'ja': 'ウォルター・アイザックソン',
      'en': 'Walter Isaacson'
    },
    category: "Biography",
    award: {
      'zh-CN': '金融时报商业图书奖',
      'zh-TW': '金融時報商業圖書獎',
      'ja': 'フィナンシャル・タイムズ・ビジネス・ブック賞',
      'en': 'Financial Times Business Book'
    },
    year: 2011,
    coverImage: "/images/books/steve-jobs.jpg",
    description: {
      'zh-CN': '基于与乔布斯本人的访谈撰写的独家传记。',
      'zh-TW': '基於與賈伯斯本人的訪談撰寫的獨家傳記。',
      'ja': 'ジョブズ本人とのインタビューに基づいた独占的伝記。',
      'en': 'The exclusive biography of Steve Jobs, based on interviews with Jobs himself.'
    }
  },
  {
    id: "15",
    title: {
      'zh-CN': '成为',
      'zh-TW': '成為這樣的我',
      'ja': 'ビカミング',
      'en': 'Becoming'
    },
    author: {
      'zh-CN': '米歇尔·奥巴马',
      'zh-TW': '蜜雪兒·歐巴馬',
      'ja': 'ミシェル・オバマ',
      'en': 'Michelle Obama'
    },
    category: "Biography",
    award: {
      'zh-CN': 'Goodreads 读者选择奖',
      'zh-TW': 'Goodreads 讀者選擇獎',
      'ja': 'Goodreads Choice Award',
      'en': 'Goodreads Choice Award'
    },
    year: 2018,
    coverImage: "/images/books/becoming.jpg",
    description: {
      'zh-CN': '美国前第一夫人的回忆录。',
      'zh-TW': '美國前第一夫人的回憶錄。',
      'ja': 'アメリカ合衆国の元ファーストレディによる回顧録。',
      'en': 'A memoir by the former First Lady of the United States.'
    }
  },
  {
    id: "16",
    title: {
      'zh-CN': '列奥纳多·达·芬奇传',
      'zh-TW': '李奧納多·達文西傳',
      'ja': 'レオナルド・ダ・ヴィンチ',
      'en': 'Leonardo da Vinci'
    },
    author: {
      'zh-CN': '沃尔特·艾萨克森',
      'zh-TW': '沃爾特·艾薩克森',
      'ja': 'ウォルター・アイザックソン',
      'en': 'Walter Isaacson'
    },
    category: "Biography",
    award: {
      'zh-CN': 'Goodreads 读者选择奖',
      'zh-TW': 'Goodreads 讀者選擇獎',
      'ja': 'Goodreads Choice Award',
      'en': 'Goodreads Choice Award'
    },
    year: 2017,
    coverImage: "/images/books/leonardo.jpg",
    description: {
      'zh-CN': '文艺复兴时期代表人物达·芬奇的传记。',
      'zh-TW': '文藝復興時期代表人物達文西的傳記。',
      'ja': 'ルネサンス人の典型であるレオナルド・ダ・ヴィンチの伝記。',
      'en': 'The biography of Leonardo da Vinci, the epitome of the Renaissance man.'
    }
  }
];