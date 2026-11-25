import { useEffect, useState } from "react";
import { curatedPizzaImage, pizzaImage, srcSetFor } from "../lib/images";

/**
 * Pizza photo with a fallback chain:
 * stored absolute URL → curated photo → neutral placeholder.
 * Fades in once loaded so the grid never flashes broken images.
 */
export default function PizzaImage({ pizza, width = 800, sizes = "(min-width: 1280px) 25vw, (min-width: 640px) 50vw, 100vw", className = "", alt, ...rest }) {
  const primary = pizzaImage(pizza, width);
  const [src, setSrc] = useState(primary);
  const [failed, setFailed] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    setSrc(primary);
    setFailed(false);
    setLoaded(false);
  }, [primary]);

  const onError = () => {
    const curated = curatedPizzaImage(pizza, width);
    if (src !== curated) setSrc(curated);
    else setFailed(true);
  };

  if (failed) {
    return (
      <div className={`grid place-items-center bg-gradient-to-br from-amber-100 to-brand-100 text-4xl ${className}`} aria-hidden="true">
        🍕
      </div>
    );
  }

  return (
    <img
      src={src}
      srcSet={srcSetFor(src)}
      sizes={srcSetFor(src) ? sizes : undefined}
      alt={alt ?? pizza?.name ?? ""}
      loading="lazy"
      decoding="async"
      onLoad={() => setLoaded(true)}
      onError={onError}
      className={`bg-surface-2 object-cover transition-opacity duration-500 ${loaded ? "opacity-100" : "opacity-0"} ${className}`}
      {...rest}
    />
  );
}
