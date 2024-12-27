const page = async ({params}: { params: Promise<{ id: string }>; }) => {
  const p = await params;
  return (
    <div>user detail page: {p.id}</div>

  )
}
export default page;