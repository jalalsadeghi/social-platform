import api from "@/services/api";

export interface ScrapeResult {
  title: string;
  description: string;
  ai_content: string;
  media_urls: string[];
}

export const scrapeProduct = async (url: string): Promise<ScrapeResult> => {
  const response = await api.post<ScrapeResult>("/products/scrape/", null, {
    params: { url },
  });

  return response.data;
};
