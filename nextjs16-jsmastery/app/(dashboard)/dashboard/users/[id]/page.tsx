export default async function Page({params} : {params: Promise<{id: string}>}) {
  const {id} = await params;

  return (
    <>
      <h1>Showing UserDetails for ID: {id}</h1>
    </>
  );
}
