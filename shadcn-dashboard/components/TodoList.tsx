"use client"

import { useState } from "react";
import { Card } from "./ui/card";
import { Checkbox } from "./ui/checkbox";
import { ScrollArea } from "./ui/scroll-area";
import { Calendar } from "./ui/calendar";
import { Popover, PopoverContent } from "./ui/popover";
import { PopoverTrigger } from "@radix-ui/react-popover";
import { CalendarIcon } from "lucide-react";
import { format, set } from "date-fns";
import { Button } from "./ui/button";


const todoList = [
  { id: "1", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "2", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "3", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "4", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "5", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "6", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "7", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "8", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "9", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "10", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "11", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "12", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "13", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "14", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "15", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "16", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "17", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "18", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "19", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
  { id: "20", title: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。" },
]

export default function TodoList() {
  const [date, setDate] = useState<Date | undefined>(new Date());
  const [open, setOpen] = useState(false);
  return (
    <>
      <h1 className="text-lg font-medium mb-6">TodoList</h1>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button className="w-full">
            <CalendarIcon />
            {date ? format(date, 'PPP') : <span>Pick a date</span>}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="p-0 w-auto">
          <Calendar mode="single" selected={date} onSelect={(date) => {
            setDate(date);
            setOpen(false);
          }}
          />
        </PopoverContent>
      </Popover>

      <ScrollArea className="max-h-[600px] mt-4 overflow-y-auto">
        <div className="flex flex-col gap-2">
          {todoList.map(item => (
            <Card key={item.id} className="p-4">
              <div className="flex items-center gap-4">
                <Checkbox id={item.id} />
                <label htmlFor={item.id} className="text-sm text-muted-foreground">{item.title}</label>
              </div>
            </Card>
          ))}
        </div>
      </ScrollArea>
    </>
  )
}