import { formatDate } from "@/lib/utils";
import { EyeIcon } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

function StartupCard({ post }: { post: StartupCardType }) {
  return (
    <li className="startup-card group">
      <div className="flext-between">
        {formatDate(post._createdAt)}
      </div>

      <div className="flex gap-1 5">
        <EyeIcon className="size-6 text-primary" />
        <span className="text-16-medium">{post.views}</span>
      </div>

      <div className="flex-between mt-5 gap-5">
        <div className="flex-1">
          <Link href={`/users/${post.author?._id}`}>
            <p className="text-16-medium line-clamp-2">{post.author?.name}</p>
          </Link>

          <Link href={`/startups/${post._id}`}>
            <h3 className="text-26-semibold line-clamp-1">{post.title}</h3>
          </Link>
        </div>

        <Link href={`/users/${post.author?._id}`}>
          <Image className="rounded-full" unoptimized
           src="https://placehold.co/48x48" alt="placeholder" width={48} height={48} />
        </Link>
      </div>

      <Link href={`/startup/${post._id}`}>
        <p className="startup-card_desc">
          {post.description}
        </p>

        <img src={post.image} alt={post.title} className="startup-card_image" />
      </Link>
    </li>
  )
}
export default StartupCard;