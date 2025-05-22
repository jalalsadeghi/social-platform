// src/components/products/ProductItem.tsx
import type { Product } from "@/services/product";

interface Props {
  product: Product;
}

export const ProductItem = ({ product }: Props) => (
  <tr>
    <td><img src={product.media[0]?.media_url} alt={product.title} className="w-12 h-12 object-cover"/></td>
    <td>{product.title}</td>
    <td>{product.instagram_stats?.views || 0}</td>
    <td>{product.instagram_stats?.likes || 0}</td>
    <td className={product.instagram_stats && product.instagram_stats.comments > 0 ? 'text-red-500' : ''}>
      {product.instagram_stats?.comments || 0}
    </td>
    <td>
      {product.status === "ready" ? (
        <span className="inline-block rounded bg-green-200 px-2 py-1 text-xs font-semibold text-green-800">
          Ready
        </span>
      ) : (
        <span className="inline-block rounded bg-gray-200 px-2 py-1 text-xs font-semibold text-gray-800">
          Pending
        </span>
      )}
    </td>
    <td>
      {/* Add Edit/Delete buttons here */}
    </td>
  </tr>
);
