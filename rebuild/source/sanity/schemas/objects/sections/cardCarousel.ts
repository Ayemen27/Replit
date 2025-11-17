import { defineType } from 'sanity'

export default defineType({
  name: 'cardCarouselSection',
  title: 'Card Carousel',
  type: 'object',
  fields: [
    {
      name: 'heading',
      title: 'Heading',
      type: 'string',
      validation: (Rule) => Rule.max(150),
    },
    {
      name: 'description',
      title: 'Description',
      type: 'text',
      rows: 3,
    },
    {
      name: 'cards',
      title: 'Cards',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            {
              name: 'image',
              title: 'Image',
              type: 'customImage',
            },
            {
              name: 'title',
              title: 'Title',
              type: 'string',
              validation: (Rule) => Rule.required().max(100),
            },
            {
              name: 'description',
              title: 'Description',
              type: 'text',
              rows: 3,
              validation: (Rule) => Rule.max(300),
            },
            {
              name: 'link',
              title: 'Link',
              type: 'link',
            },
            {
              name: 'tags',
              title: 'Tags',
              type: 'array',
              of: [{ type: 'string' }],
              options: {
                layout: 'tags',
              },
            },
          ],
          preview: {
            select: {
              title: 'title',
              media: 'image',
            },
          },
        },
      ],
      validation: (Rule) => Rule.min(1).max(20),
    },
    {
      name: 'autoplay',
      title: 'Autoplay',
      type: 'boolean',
      initialValue: false,
    },
    {
      name: 'loop',
      title: 'Loop',
      type: 'boolean',
      initialValue: true,
    },
    {
      name: 'slidesPerView',
      title: 'Slides Per View',
      type: 'number',
      validation: (Rule) => Rule.min(1).max(6).integer(),
      initialValue: 3,
    },
  ],
  preview: {
    select: {
      title: 'heading',
      cardCount: 'cards',
    },
    prepare({ title, cardCount }) {
      return {
        title: title || 'Card Carousel',
        subtitle: cardCount ? `${cardCount.length} cards` : 'No cards',
      }
    },
  },
})
