import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: '铁路12306 - 中国铁路客户服务中心',
  description: '中国铁路客户服务中心官方网站，提供全国列车时刻表查询、火车票预订、在线订票、退票改签、高铁票查询等服务',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>{children}</body>
    </html>
  )
}