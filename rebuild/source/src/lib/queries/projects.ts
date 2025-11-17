export const projectsQuery = `
  *[_type == "project" && isPublished == true] | order(_createdAt desc) {
    _id,
    _type,
    title,
    slug,
    description,
    image {
      asset->,
      alt
    },
    demoUrl,
    replUrl,
    category->{
      _id,
      name,
      slug,
      icon,
      color
    },
    tags,
    isFeatured,
    viewsCount,
    likesCount,
    _createdAt,
    _updatedAt
  }
`;

export const featuredProjectsQuery = `
  *[_type == "project" && isPublished == true && isFeatured == true] | order(_createdAt desc) [0...6] {
    _id,
    _type,
    title,
    slug,
    description,
    image {
      asset->,
      alt
    },
    demoUrl,
    replUrl,
    category->{
      _id,
      name,
      slug,
      icon,
      color
    },
    tags,
    viewsCount,
    likesCount,
    _createdAt
  }
`;

export const projectBySlugQuery = `
  *[_type == "project" && slug.current == $slug && isPublished == true][0] {
    _id,
    _type,
    title,
    slug,
    description,
    image {
      asset->,
      alt
    },
    demoUrl,
    replUrl,
    category->{
      _id,
      name,
      slug,
      icon,
      color
    },
    tags,
    viewsCount,
    likesCount,
    _createdAt,
    _updatedAt
  }
`;

export const projectsByCategoryQuery = `
  *[_type == "project" && isPublished == true && category->slug.current == $categorySlug] | order(_createdAt desc) {
    _id,
    _type,
    title,
    slug,
    description,
    image {
      asset->,
      alt
    },
    demoUrl,
    replUrl,
    category->{
      _id,
      name,
      slug,
      icon,
      color
    },
    tags,
    viewsCount,
    likesCount,
    _createdAt
  }
`;
