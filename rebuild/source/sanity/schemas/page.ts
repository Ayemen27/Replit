import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'page',
  title: 'Page',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: 'Title',
      type: 'string',
      validation: (Rule) => Rule.required().max(150),
    }),
    defineField({
      name: 'slug',
      title: 'Slug',
      type: 'slug',
      options: {
        source: 'title',
        maxLength: 96,
      },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'sections',
      title: 'Page Sections',
      type: 'array',
      description: 'Build your page by adding sections',
      of: [
        { type: 'heroSection' },
        { type: 'standardTextSection' },
        { type: 'valuePropGridSection' },
        { type: 'cardCarouselSection' },
        { type: 'alternatingEditorialSection' },
        { type: 'statsSection' },
        { type: 'pricingTableSection' },
        { type: 'faqSection' },
        { type: 'testimonialSection' },
        { type: 'ctaBandSection' },
        { type: 'teamGridSection' },
        { type: 'logoGridSection' },
        { type: 'metricsStripSection' },
        { type: 'formSection' },
        { type: 'knowledgeBaseSearchSection' },
        { type: 'galleryFilterGridSection' },
        { type: 'articleHeaderSection' },
        { type: 'relatedContentSection' },
        { type: 'tableOfContentsSection' },
        { type: 'codeEmbedSection' },
        { type: 'commentsSection' },
      ],
    }),
    defineField({
      name: 'seo',
      title: 'SEO',
      type: 'object',
      fields: [
        {
          name: 'title',
          title: 'SEO Title',
          type: 'string',
          description: 'Override the page title for search engines',
          validation: (Rule) => Rule.max(60),
        },
        {
          name: 'description',
          title: 'SEO Description',
          type: 'text',
          rows: 3,
          description: 'Meta description for search engines',
          validation: (Rule) => Rule.max(160),
        },
        {
          name: 'ogImage',
          title: 'Open Graph Image',
          type: 'image',
          description: 'Image for social media sharing (1200x630px recommended)',
          options: {
            hotspot: true,
          },
          fields: [
            {
              name: 'alt',
              type: 'string',
              title: 'Alternative Text',
            },
          ],
        },
      ],
      options: {
        collapsible: true,
        collapsed: false,
      },
    }),
    defineField({
      name: 'isPublished',
      title: 'Is Published',
      type: 'boolean',
      initialValue: true,
    }),
  ],
  preview: {
    select: {
      title: 'title',
      slug: 'slug.current',
      published: 'isPublished',
    },
    prepare({ title, slug, published }) {
      return {
        title,
        subtitle: `/${slug} ${published ? '✓' : '(Draft)'}`,
      }
    },
  },
  orderings: [
    {
      title: 'Title A-Z',
      name: 'titleAsc',
      by: [{ field: 'title', direction: 'asc' }],
    },
    {
      title: 'Most Recent',
      name: 'createdAtDesc',
      by: [{ field: '_createdAt', direction: 'desc' }],
    },
  ],
})
