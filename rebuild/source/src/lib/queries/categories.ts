export const categoriesQuery = `
  *[_type == "category"] | order(order asc, name asc) {
    _id,
    _type,
    name,
    slug,
    description,
    icon,
    color,
    order
  }
`;

export const categoryBySlugQuery = `
  *[_type == "category" && slug.current == $slug][0] {
    _id,
    _type,
    name,
    slug,
    description,
    icon,
    color,
    order
  }
`;
