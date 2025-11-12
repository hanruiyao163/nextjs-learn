import Event from "@/database/event.model";
import connectDB from "@/lib/mongodb";
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    await connectDB();

    const formData = await req.formData();
    let event;
    try {
      event = Object.fromEntries(formData.entries());
    } catch (e) {
      return NextResponse.json({message: "Invalid JSON data format"}, {status: 400});
    }

    const createdEvent = await Event.create(event);
  } catch (e) {
    console.error(e);
    return NextResponse.json({ message: "Event Creation Failed", error: e instanceof Error ? e.message : "Unknown" });
  }

}

