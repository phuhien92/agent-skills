# Worked example: news feed

Locked in the 2026 practice session. Reuse the *shape*, not the product, for autocomplete, Pinterest, chat, docs, etc.

## Opening question

Interviewer: “Design a news feed. Reddit, Twitter, etc.”

Coach asks: first 3–5 clarifying questions, then lock FR/NFR.

## Locked R

**Core FR:** browse allowed posts (self / friends / public); create text or image; visibility public | friends-only | private; like/react; infinite scroll.

**Nice-to-have:** comments, share, live updates.

**Core NFR:** mobile-first responsive web; fast first paint / prefetch next page; smooth after hundreds of posts; like and create feel instant.

**Park:** native app, SEO, offline, i18n. A11y is an O deep-dive, not an architecture constraint.

## Locked A

```
Server (GET /feed, POST /posts, set reaction)
        ▲
Data access (React Query: fetch, cache, retry, errors)
        ▲
Feed UI
  ├─ Composer (always on) — local draft: content, visibility, image File
  └─ Post list — reads cache; sentinel at tail
       └─ Post item — presenter; emits like
```

Composer has no modal. “Near bottom” is a **sentinel**, not a site footer.

## Locked D

```ts
type PostVisibility = 'public' | 'friends-only' | 'private'
type User = { id: string; displayName: string; profilePhotoUrl: string }
type Post = {
  id: string
  createdAt: string
  content: string
  imageUrl?: string
  imageWidth?: number
  imageHeight?: number
  visibility: PostVisibility
  author: User
  likeCount: number
  myReaction: boolean
}
type FeedPage = { posts: Post[]; nextCursor: string | null; hasMore: boolean }
type NewPost = { content: string; visibility: PostVisibility; image?: File }
```

`NewPost` has no `id` / `author` / `createdAt`. Session identifies the user.

## Locked I

- `GET /feed?limit=&cursor=` — omit `cursor` on first request. Response is `FeedPage`.
- `POST /posts` — body `NewPost` (multipart if file). Response is `Post`.
- Set reaction: `{ liked: boolean }` → `{ likeCount, myReaction }`. Never send `likeCount` from the client.

Why not `?page=2`: feed mutates at the top; offset duplicates or skips.

## Locked O (order)

1. First fetch: **skeleton cards**. Next page fail: keep rows, retry at bottom.
2. Prefetch: sentinel + `rootMargin` ~one viewport. Guard: `hasMore && !isFetchingNextPage`.
3. Virtualize at hundreds/thousands of posts: cache stays large; DOM is a window + spacer + overscan; estimate then `measureElement`; remesasure if you did not reserve image space.
4. Images: API width/height → `aspect-ratio`. Placeholder sits *inside* the box.
5. Optimistic prepend create / flip like; rollback on fail. If composer is always on, do not clobber a new draft (toast or Retry card).
6. `role="feed"` on the list, `<article>` per post, like is a `<button>`, image `alt`.
7. Caption is **plain text** (React escaping + `pre-wrap`). No raw HTML. Markdown still needs sanitize.

**CSR vs SSR (one sentence):** CSR + skeletons = one data path, worse LCP. Hybrid = SSR shell or first page, CSR for scroll. Do not SSR every page.

## High-value holes after RADIO

- Disable Publish while `isPending` and when draft is empty (no double POST).
- `limit ≈ ceil(viewport / estimate) + buffer`.
- XSS on UGC (above).
- Be able to say the file’s **hybrid** answer even if you picked CSR.
- Normalized store only if comments make the same `User` appear many times.
- Live comments only if pulled back in scope: SSE or WebSocket, not short poll.

## First-question templates (any product)

- “Which surface of this product are we designing?”
- “What can the user do in 45 minutes vs park?”
- “Which NFRs change the *client* (list scale, first paint, realtime)?”
- “Where does server data vs draft vs chrome state live?”
- “How do we page, and why not offset?”
- “What is unique to optimize — not generic minification?”
