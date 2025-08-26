"use client"

import { useForm } from "react-hook-form";
import { SheetContent, SheetDescription, SheetHeader, SheetTitle } from "./ui/sheet"
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

const formSchema = z.object({
  email: z.email("Invalid email address"),
  username: z.string().min(2, "Username must be at least 2 characters long").max(50, "Username must be at most 50 characters long"),
  phone: z.string().min(10, "Phone number must be at least 10 characters long").max(15, "Phone number must be at most 15 characters long"),
  role: z.enum(["user", "admin"], "Invalid role"),
});



export default function EditUser() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      username: "john.doe",
      phone: "+1234567890",
      role: "admin",
    }
  });
  console.log("form", {...form})
  return (
    <SheetContent>
      <SheetHeader>
        <SheetTitle>Edit User</SheetTitle>

        <SheetDescription>

        </SheetDescription>
      </SheetHeader>
    </SheetContent>
  )
}