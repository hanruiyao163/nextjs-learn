const page = ({params}: {params: {id: string}}) => {
  return (
    <div>user detail page: {params.id}</div>
    
  )
}
export default page