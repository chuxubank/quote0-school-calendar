import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://quote0-school-calendar.chuxubank.chatgpt.site"),
  title: "沪上校历｜Quote/0 上海中小学校历插件",
  description: "为 Quote/0 墨水屏设计的上海中小学校历插件，显示开学多久、距离学期结束还有多久，以及寒暑假进度。",
  openGraph: {
    title: "沪上校历｜Quote/0 上海中小学校历插件",
    description: "把上海中小学的开学、结课和寒暑假进度放进 296 × 152。",
    type: "website",
    locale: "zh_CN",
    images: [
      {
        url: "/og.png",
        width: 1536,
        height: 1024,
        alt: "沪上校历 Quote/0 插件",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "沪上校历｜Quote/0 上海中小学校历插件",
    description: "上海中小学开学、结课与寒暑假进度。",
    images: ["/og.png"],
  },
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
