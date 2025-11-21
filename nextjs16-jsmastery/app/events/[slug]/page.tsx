import Image from "next/image";
import { notFound } from "next/navigation";

const BASE_URL = process.env.BASE_URL;

export default async function EventDetails({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;

  const request = await fetch(`${BASE_URL}/api/events/${slug}`);
  const { event } = await request.json();

  if (!event)  return notFound();

  return (
    <section id="event">
      <div className="header">
        <h1>Event Description</h1>
        <p className="mt-2">{event.description}</p>
      </div>

      <div className="details">
        {/* left */}
        <div className="content">
          <Image src={event.image} alt="Event Banner" width={800} height={800} className="banner" />

          <section className="flex-col-gap-2">
          <h2>Overview</h2>
          <p>{event.overview}</p>
          </section>

          <section className="flex-col-gap-2"></section>
        </div>


        {/* right */}
        <aside className="booking">
          <p className="text-lg font-semibold">

          </p>
        </aside>

      </div>
    </section>
  );
}


function EventDetailsItem() {
  
  return (
    <></>
  );
}


