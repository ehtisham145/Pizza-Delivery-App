import { reviewApi } from "../api/endpoints";
import { Alert, Empty, PageHeader, Spinner, dateTime, shortId, useLoad } from "../components/ui";

export function Stars({ rating }) {
  const r = Math.round(Number(rating) || 0);
  return (
    <span className="stars" aria-label={`${r} out of 5`}>
      {"★".repeat(r)}
      {"☆".repeat(5 - r)}
    </span>
  );
}

export default function MyReviews() {
  const list = useLoad(() => reviewApi.mine());
  const reviews = list.data || [];

  return (
    <>
      <PageHeader title="My reviews" subtitle="Reviews you've written for delivered orders." />
      {list.loading && <Spinner />}
      <Alert type="error">{list.error}</Alert>
      {!list.loading && !list.error && reviews.length === 0 && (
        <Empty icon="⭐" title="No reviews yet">
          Open a delivered order to write one.
        </Empty>
      )}
      <ul className="review-list">
        {reviews.map((r) => (
          <li key={r.id} className="card review">
            <div className="review-head">
              <strong>Order #{shortId(r.order_id)}</strong>
              <Stars rating={r.rating} />
            </div>
            {r.comment && <p>{r.comment}</p>}
            <span className="muted small">{dateTime(r.created_at)}</span>
          </li>
        ))}
      </ul>
    </>
  );
}
