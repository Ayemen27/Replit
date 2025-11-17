export const useCasesQuery = `
  *[_type == "useCase"] | order(order asc, title asc) {
    _id,
    _type,
    title,
    slug,
    description,
    icon,
    image {
      asset->,
      alt
    },
    features,
    order
  }
`;

export const useCaseBySlugQuery = `
  *[_type == "useCase" && slug.current == $slug][0] {
    _id,
    _type,
    title,
    slug,
    description,
    icon,
    image {
      asset->,
      alt
    },
    features,
    order
  }
`;
