"use client"

import { DropdownMenuSubTrigger, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { DropdownMenu } from "@/components/ui/dropdown-menu";
import { ColumnDef } from "@tanstack/react-table"
import { Button } from "@/components/ui/button";
import { MoreHorizontal } from "lucide-react";

// This type is used to define the shape of our data.
// You can use a Zod schema here if you want.
export type Payment = {
  id: string;
  amount: number;
  status: "pending" | "processing" | "success" | "failed";
  email: string;
  username: string;
  phone?: string;
};

export const columns: ColumnDef<Payment>[] = [
  {
    accessorKey: "username",
    header: "User",
  },
  {
    // accessorKey: "status",
    header: "Status",
    accessorFn: row => row.status,
    cell: ({ row }) => {
      const status = row.getValue("status") as string;
      return (
        <div className={cn(`p-1 rounded-md w-max text-xs`,
          status === "pending" && "bg-yellow-500/40",
          status === "success" && "bg-green-500/40",
          status === "failed" && "bg-red-500/40"
        )}>
          {status}
        </div>
      )
    }
  },
  {
    accessorKey: "email",
    header: "Email",
  },
  {
    accessorKey: "amount",
    header: () => <div className="text-right">Amount</div>,
    cell: (cell) => {
      console.log("cell value", cell.getValue());
      const amount = parseFloat(cell.row.getValue("amount"));
      const formatted = new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(amount);
      return <div className="text-right">{formatted}</div>;
    }
  },
  {
    id: "actions",
    cell: ({row}) => {
      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant={"ghost"} className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
        </DropdownMenu>
      )
    }
  }
]