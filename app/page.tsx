'use client';

import { useState } from 'react';
import { books, categories } from '@/lib/books-data';
import { BookCard } from '@/components/BookCard';
import { Button } from '@/components/ui/button';
import { BookOpen, Library, Globe } from 'lucide-react';
import { Language, translations, languageNames } from '@/lib/translations';
import { DropdownMenu, DropdownMenuItem } from '@/components/ui/dropdown-menu';

export default function Home() {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [language, setLanguage] = useState<Language>('zh-CN');

  const t = translations[language];
  const categoryMap: Record<string, string> = {
    'All': t.categories.all,
    'Fiction': t.categories.fiction,
    'Non-Fiction': t.categories.nonFiction,
    'Mystery': t.categories.mystery,
    'Science Fiction': t.categories.scienceFiction,
    'Biography': t.categories.biography
  };

  const filteredBooks = selectedCategory === 'All' 
    ? books 
    : books.filter(book => book.category === selectedCategory);

  return (
    <main className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-shelf-wood-dark via-literary-burgundy to-literary-navy py-24 px-6 overflow-hidden">
        <div className="absolute inset-0 bg-black/40"></div>
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMC41IiBvcGFjaXR5PSIwLjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-10"></div>
        
        <div className="container mx-auto max-w-7xl relative">
          {/* Language Switcher */}
          <div className="absolute top-0 right-0">
            <DropdownMenu
              trigger={
                <Button variant="outline" className="gap-2 bg-white/10 border-white/20 text-white hover:bg-white/20">
                  <Globe className="w-4 h-4" />
                  {languageNames[language]}
                </Button>
              }
            >
              {(Object.keys(languageNames) as Language[]).map((lang) => (
                <DropdownMenuItem
                  key={lang}
                  onClick={() => setLanguage(lang)}
                  className={language === lang ? 'bg-accent' : ''}
                >
                  {languageNames[lang]}
                </DropdownMenuItem>
              ))}
            </DropdownMenu>
          </div>

          <div className="flex items-center justify-center mb-6">
            <Library className="w-16 h-16 text-literary-gold drop-shadow-lg" />
          </div>
          <h1 className="text-6xl md:text-7xl font-bold text-center mb-6 tracking-tight leading-none text-white drop-shadow-2xl">
            {t.hero.title}
            <span className="block text-literary-gold mt-2 drop-shadow-lg">{t.hero.titleAccent}</span>
          </h1>
          <p className="text-xl text-center max-w-2xl mx-auto text-white/95 leading-relaxed drop-shadow-lg">
            {t.hero.subtitle}
          </p>
        </div>
      </section>

      {/* Filter Section */}
      <section className="border-b border-border bg-card sticky top-0 z-10 shadow-sm">
        <div className="container mx-auto max-w-7xl px-6 py-6">
          <div className="flex items-center gap-3 mb-4">
            <BookOpen className="w-5 h-5 text-literary-gold" />
            <h2 className="text-lg font-semibold">{t.categories.browseByCategory}</h2>
          </div>
          <div className="flex flex-wrap gap-3">
            {categories.map((category) => (
              <Button
                key={category}
                variant={selectedCategory === category ? "default" : "outline"}
                onClick={() => setSelectedCategory(category)}
                className="transition-all duration-200"
              >
                {categoryMap[category]}
                {selectedCategory === category && (
                  <span className="ml-2 text-xs bg-primary-foreground/20 px-2 py-0.5 rounded-full">
                    {category === 'All' ? books.length : books.filter(b => b.category === category).length}
                  </span>
                )}
              </Button>
            ))}
          </div>
        </div>
      </section>

      {/* Books Grid */}
      <section className="container mx-auto max-w-7xl px-6 py-16">
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2">
            {selectedCategory === 'All' ? t.books.allBooks : categoryMap[selectedCategory]}
          </h2>
          <p className="text-muted-foreground">
            {filteredBooks.length} {filteredBooks.length === 1 ? t.books.book : t.books.books} {t.books.available}
          </p>
        </div>
        
        {filteredBooks.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
            {filteredBooks.map((book) => (
              <BookCard key={book.id} book={book} awardWinnerText={t.books.awardWinner} language={language} />
            ))}
          </div>
        ) : (
          <div className="text-center py-24">
            <BookOpen className="w-16 h-16 text-muted-foreground/50 mx-auto mb-4" />
            <p className="text-xl text-muted-foreground">{t.books.noBooks}</p>
          </div>
        )}
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-card mt-24">
        <div className="container mx-auto max-w-7xl px-6 py-12">
          <div className="flex items-center justify-center gap-2 text-muted-foreground">
            <Library className="w-5 h-5" />
            <p className="text-sm">{t.footer.curatedCollection}</p>
          </div>
        </div>
      </footer>
    </main>
  );
}