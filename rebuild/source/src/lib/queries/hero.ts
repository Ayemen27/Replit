export const heroByKeyQuery = `
  *[_type == "heroSection" && key == $key][0] {
    _id,
    _type,
    key,
    title,
    subtitle,
    description,
    ctaText,
    ctaUrl,
    backgroundImage {
      asset->,
      alt
    },
    backgroundVideo
  }
`;
