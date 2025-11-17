export const newsPostsQuery = `
  *[_type == "newsPost" && isPublished == true] | order(publishedAt desc) {
    _id,
    _type,
    title,
    slug,
    excerpt,
    coverImage {
      asset->,
      alt
    },
    author {
      name,
      image {
        asset->
      }
    },
    publishedAt,
    category,
    _createdAt
  }
`;

export const newsPostBySlugQuery = `
  *[_type == "newsPost" && slug.current == $slug && isPublished == true][0] {
    _id,
    _type,
    title,
    slug,
    excerpt,
    coverImage {
      asset->,
      alt
    },
    author {
      name,
      image {
        asset->
      }
    },
    publishedAt,
    category,
    _createdAt
  }
`;

export const recentNewsQuery = `
  *[_type == "newsPost" && isPublished == true] | order(publishedAt desc) [0...5] {
    _id,
    _type,
    title,
    slug,
    excerpt,
    coverImage {
      asset->,
      alt
    },
    publishedAt,
    category
  }
`;
