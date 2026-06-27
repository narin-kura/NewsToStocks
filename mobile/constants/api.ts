import Constants from "expo-constants";

// Resolution order:
//   1. EXPO_PUBLIC_API_URL  — set at build time (e.g. in eas.json env)
//   2. app.json > expo.extra.apiUrl  — the MarketSignal (NewsToStocks) Cloud Run URL
//   3. localhost  — local dev fallback
// Production points at GCP Cloud Run (not the HF Space).
export const API_BASE =
  process.env.EXPO_PUBLIC_API_URL ??
  (Constants.expoConfig?.extra?.apiUrl as string) ??
  "http://localhost:7860";

// ----- Shared response types (mirror the Flask /api JSON) -----
export type Price = { price: number; change_pct: number | null } | null;

export type Article = { preview: string; url: string; source?: string | null };

export type Signal = {
  symbol: string;
  company_name?: string | null;
  mentions: number;
  avg_sentiment: number;
  price: Price;
  articles: Article[];
  neg_articles: Article[];
};

export type Performance = { up: number; down: number; flat: number; total: number };

export type SignalsResponse = {
  sector: string;
  sort: string;
  cache_age_min: number;
  articles_count: number;
  performance: Performance;
  signals: Signal[];
};

export type Tab = { key: string; label: string };

export type TabsResponse = { tabs: Tab[]; sorts: Tab[] };

export type SearchResponse = {
  query: string;
  found: boolean;
  cache_age_min: number;
  result: Signal | null;
};
