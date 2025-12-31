'use client';

import { Book } from "@/lib/books-data";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Award, Calendar, User } from "lucide-react";
import { useState } from "react";
import { Language } from "@/lib/translations";

interface BookCardProps {
  book: Book;
  awardWinnerText: string;
  language: Language;
}

export function BookCard({ book, awardWinnerText, language }: BookCardProps) {
  const [imageError, setImageError] = useState(false);

  return (
    <Card className="group overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
      <div className="relative h-64 bg-gradient-to-br from-muted to-accent overflow-hidden">
        {!imageError ? (
          <img
            src={book.coverImage}
            alt={book.title[language]}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            onError={() => setImageError(true)}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-literary-burgundy/20 to-literary-navy/20">
            <div className="text-center p-8">
              <h3 className="text-2xl font-bold text-foreground/80 mb-2 leading-tight">{book.title[language]}</h3>
              <p className="text-sm text-muted-foreground">{book.author[language]}</p>
            </div>
          </div>
        )}
        <div className="absolute top-3 right-3">
          <Badge variant="literary">
            <Award className="w-3 h-3 mr-1" />
            {awardWinnerText}
          </Badge>
        </div>
      </div>
      
      <CardHeader className="space-y-3">
        <CardTitle className="text-xl leading-tight line-clamp-2">{book.title[language]}</CardTitle>
        <div className="flex flex-col gap-2 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <User className="w-4 h-4" />
            <span className="font-medium">{book.author[language]}</span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            <span>{book.year}</span>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <CardDescription className="line-clamp-3 leading-relaxed">
          {book.description[language]}
        </CardDescription>
        <div className="mt-4 pt-4 border-t border-border">
          <div className="flex items-center justify-between">
            <Badge variant="outline" className="text-xs">
              {book.category}
            </Badge>
            <span className="text-xs text-literary-gold font-semibold tracking-wide">
              {book.award[language]}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}