// frontend/src/pages/ProductPage.tsx
import { ProductTable } from "@/components/products/ProductTable";
import { ProductDialog } from "@/components/products/ProductDialog";

const ProductPage = () => {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <ProductDialog open={false} onClose={() => {}} />
        <input placeholder="Search..." className="border rounded p-2" />
      </div>
      <ProductTable />
    </div>
  );
};

export default ProductPage;
