import { defineType } from 'sanity'

export default defineType({
  name: 'contentReference',
  title: 'Content Reference',
  type: 'object',
  fields: [
    {
      name: 'reference',
      title: 'Reference',
      type: 'reference',
      to: [
        { type: 'page' },
        { type: 'newsPost' },
        { type: 'customerStory' },
        { type: 'productPage' },
        { type: 'project' },
        { type: 'useCase' },
      ],
      description: 'Link to another content item',
    },
    {
      name: 'title',
      title: 'Custom Title',
      type: 'string',
      description: 'Override the default title from the referenced content',
      validation: (Rule) => Rule.max(150),
    },
    {
      name: 'description',
      title: 'Custom Description',
      type: 'text',
      rows: 3,
      description: 'Override the default description from the referenced content',
      validation: (Rule) => Rule.max(300),
    },
    {
      name: 'image',
      title: 'Custom Image',
      type: 'customImage',
      description: 'Override the default image from the referenced content',
    },
  ],
  preview: {
    select: {
      title: 'title',
      refTitle: 'reference.title',
      media: 'image',
      refMedia: 'reference.coverImage',
    },
    prepare({ title, refTitle, media, refMedia }) {
      return {
        title: title || refTitle || 'Content Reference',
        media: media || refMedia,
      }
    },
  },
})
