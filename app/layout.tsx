import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "沪上校历｜Quote/0 上海中小学校历插件",
  description: "为 Quote/0 墨水屏设计的上海中小学校历插件，显示开学多久、距离学期结束还有多久，以及寒暑假进度。",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
