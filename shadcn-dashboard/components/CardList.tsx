import Image from "next/image"
import { Card, CardContent, CardFooter, CardTitle } from "./ui/card"
import { Badge } from "./ui/badge"

const list = [
  { id: 1, image: "https://github.com/shadcn.png", title: "Card Title1", count: 1200, badge: "john smith" },
  { id: 2, image: "https://github.com/shadcn.png", title: "Card Title2", count: 1300, badge: "john smith" },
  { id: 3, image: "https://github.com/shadcn.png", title: "Card Title3", count: 1400, badge: "john smith" },
]


export default function CardList({ title }: { title?: string }) {
  return (
    <div>
      <h1 className="text-lg font-medium mb-6">{title}</h1>
      <div className="flex flex-col gap-2">
        {
          list.map(item => (
            <Card key={item.id} className="flex-row items-center justify-between">
              <div className="w-12 h-12 rounded-sm relative overflow-hidden ml-3">
                <Image className="object-cover" src={item.image} alt={item.title} fill />
              </div>

            <CardContent className="flex-1">
              <CardTitle className="text-sm font-medium">{item.title}</CardTitle>
              <Badge variant={"secondary"}>{item.badge}</Badge>
            </CardContent>

            <CardFooter className="">
              {item.count}
            </CardFooter>

            </Card>
          ))
        }
      </div>
    </div>
  )
}
