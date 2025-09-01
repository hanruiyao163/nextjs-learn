import { columns, type Payment } from "./columns";
import { DataTable } from "./data-table";

const payments: Payment[] = [
  {
    id: "728ed52f",
    amount: 100,
    status: "pending",
    email: "m@example.com",
    username: "Alice",
    phone: "+1234567890",
  },
  {
    id: "489e1d42",
    amount: 125,
    status: "processing",
    email: "example@gmail.com",
    username: "Bob",
    phone: "+1987654321",
  },
  {
    id: "a1b2c3d4",
    amount: 250,
    status: "success",
    email: "user1@domain.com",
    username: "Charlie",
    phone: "+1555123456",
  },
  {
    id: "e5f6g7h8",
    amount: 75,
    status: "failed",
    email: "test@example.org",
    username: "David",
    phone: "+1444987654",
  },
  {
    id: "i9j0k1l2",
    amount: 300,
    status: "pending",
    email: "another@example.com",
    username: "Eve",
    phone: "+1777123456",
  },
  {
    id: "m3n4o5p6",
    amount: 150,
    status: "processing",
    email: "sample@site.com",
    username: "Frank",
    phone: "+1888987654",
  },
  {
    id: "q7r8s9t0",
    amount: 200,
    status: "success",
    email: "demo@company.net",
    username: "Grace",
    phone: "+1999123456",
  },
  {
    id: "u1v2w3x4",
    amount: 50,
    status: "failed",
    email: "info@web.io",
    username: "Henry",
    phone: "+1666987654",
  },
  {
    id: "728ed52f",
    amount: 100,
    status: "pending",
    email: "m@example.com",
    username: "Alice",
    phone: "+1234567890",
  },
  {
    id: "489e1d42",
    amount: 125,
    status: "processing",
    email: "example@gmail.com",
    username: "Bob",
    phone: "+1987654321",
  },
  {
    id: "a1b2c3d4",
    amount: 250,
    status: "success",
    email: "user1@domain.com",
    username: "Charlie",
    phone: "+1555123456",
  },
  {
    id: "e5f6g7h8",
    amount: 75,
    status: "failed",
    email: "test@example.org",
    username: "David",
    phone: "+1444987654",
  },
  {
    id: "i9j0k1l2",
    amount: 300,
    status: "pending",
    email: "another@example.com",
    username: "Eve",
    phone: "+1777123456",
  },
  {
    id: "m3n4o5p6",
    amount: 150,
    status: "processing",
    email: "sample@site.com",
    username: "Frank",
    phone: "+1888987654",
  },
  {
    id: "q7r8s9t0",
    amount: 200,
    status: "success",
    email: "demo@company.net",
    username: "Grace",
    phone: "+1999123456",
  },
  {
    id: "u1v2w3x4",
    amount: 50,
    status: "failed",
    email: "info@web.io",
    username: "Henry",
    phone: "+1666987654",
  },
];

const getData = async () => {
  return payments;
}

export default async function page() {
  const data = await getData();
  return (
    <div>
      <div className="mb-8 px-4 bg-secondary rounded-md">
        <h1 className="font-semibold p-2 text-center">All Payments</h1>
      </div>

      <DataTable columns={columns} data={data} />
    </div>
  )
}