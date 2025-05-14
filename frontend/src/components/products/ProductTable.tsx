// src/components/products/ProductTable.tsx
import { useState } from "react";
import InfiniteScroll from "react-infinite-scroll-component";
import { useProducts } from "@/hooks/useProducts";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  TableCaption,
} from "@/components/ui/table";
import { ProductDialog } from "@/components/products/ProductDialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ChevronDown } from "lucide-react";
import type { Product } from "@/services/product";

export const ProductTable = () => {
  const { productsQuery, deleteMutation } = useProducts();
  const { data, fetchNextPage, hasNextPage, isLoading } = productsQuery;

  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortOption, setSortOption] = useState("latest");
  const [addDialogOpen, setAddDialogOpen] = useState(false);

  const handleEditClick = (product: Product) => {
    setSelectedProduct(product);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setSelectedProduct(null);
    setDialogOpen(false);
  };

  const filteredProducts = data?.pages
    .flat()
    .filter((p) =>
      p.title.toLowerCase().includes(searchQuery.toLowerCase())
    );

  const sortedProducts = filteredProducts?.sort((a, b) => {
    switch (sortOption) {
      case "latest":
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      case "views":
        return (b.instagram_stats?.views || 0) - (a.instagram_stats?.views || 0);
      case "likes":
        return (b.instagram_stats?.likes || 0) - (a.instagram_stats?.likes || 0);
      case "comments":
        return (b.instagram_stats?.comments || 0) - (a.instagram_stats?.comments || 0);
      default:
        return 0;
    }
  });

  if (isLoading) {
    return (
      <div className="space-y-2">
        <Skeleton className="w-full h-12" />
        <Skeleton className="w-full h-12" />
        <Skeleton className="w-full h-12" />
      </div>
    );
  }

  return (
    <>
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-2">
          <Input
            placeholder="Search products..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-64"
          />
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline">
                Sort: {sortOption.charAt(0).toUpperCase() + sortOption.slice(1)}
                <ChevronDown className="ml-2 h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => setSortOption("latest")}>
                Latest
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setSortOption("views")}>
                Most Viewed
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setSortOption("likes")}>
                Most Liked
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setSortOption("comments")}>
                Most Commented
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <Button onClick={() => setAddDialogOpen(true)}>Add new</Button>
      </div>

      <InfiniteScroll
        dataLength={sortedProducts?.length || 0}
        next={fetchNextPage}
        hasMore={!!hasNextPage}
        loader={<Skeleton className="w-full h-12" />}
      >
        <Table>
          <TableCaption>A list of your products.</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[120px]">Media</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Views</TableHead>
              <TableHead>Likes</TableHead>
              <TableHead>Comments</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedProducts?.map((product) => (
              <TableRow key={product.id}>
                <TableCell>
                  <img
                    src={product.media[0]?.media_url}
                    alt={product.title}
                    className="w-12 h-12 object-cover rounded-md"
                  />
                </TableCell>
                <TableCell className="font-medium">{product.title}</TableCell>
                <TableCell>{product.instagram_stats?.views || 0}</TableCell>
                <TableCell>{product.instagram_stats?.likes || 0}</TableCell>
                <TableCell
                  className={
                    product.instagram_stats &&
                    product.instagram_stats.comments > 0
                      ? "text-red-500"
                      : ""
                  }
                >
                  {product.instagram_stats?.comments || 0}
                </TableCell>
                <TableCell className="text-right space-x-2">
                  <button
                    onClick={() => handleEditClick(product)}
                    className="text-blue-500 hover:underline"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => deleteMutation.mutate(product.id)}
                    className="text-red-500 hover:underline"
                  >
                    Delete
                  </button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </InfiniteScroll>

      {dialogOpen && selectedProduct && (
        <ProductDialog
          productId={selectedProduct.id}
          initialData={{
            title: selectedProduct.title,
            product_url: selectedProduct.product_url,
            description: selectedProduct.description,
            ai_content: selectedProduct.ai_content,
            media: selectedProduct.media.map(m => ({
              id: m.id,
              media_url: m.media_url,
              media_type: m.media_type
            }))
          }}
          open={dialogOpen}
          onClose={handleCloseDialog}
        />
      )}

      <ProductDialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} />
    </>
  );
};
