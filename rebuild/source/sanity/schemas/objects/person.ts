import { defineType } from 'sanity'

export default defineType({
  name: 'person',
  title: 'Person',
  type: 'object',
  fields: [
    {
      name: 'name',
      title: 'Name',
      type: 'string',
      validation: (Rule) => Rule.required().max(100),
    },
    {
      name: 'role',
      title: 'Role/Title',
      type: 'string',
      validation: (Rule) => Rule.max(100),
    },
    {
      name: 'bio',
      title: 'Bio',
      type: 'text',
      rows: 4,
      validation: (Rule) => Rule.max(500),
    },
    {
      name: 'image',
      title: 'Photo',
      type: 'customImage',
    },
    {
      name: 'socialLinks',
      title: 'Social Links',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            {
              name: 'platform',
              title: 'Platform',
              type: 'string',
              options: {
                list: [
                  { title: 'Twitter', value: 'twitter' },
                  { title: 'LinkedIn', value: 'linkedin' },
                  { title: 'GitHub', value: 'github' },
                  { title: 'Website', value: 'website' },
                  { title: 'Email', value: 'email' },
                  { title: 'Other', value: 'other' },
                ],
                layout: 'dropdown',
              },
              validation: (Rule) => Rule.required(),
            },
            {
              name: 'url',
              title: 'URL',
              type: 'url',
              validation: (Rule) => Rule.required(),
            },
          ],
          preview: {
            select: {
              platform: 'platform',
              url: 'url',
            },
            prepare({ platform, url }) {
              return {
                title: platform || 'Social Link',
                subtitle: url,
              }
            },
          },
        },
      ],
    },
  ],
  preview: {
    select: {
      name: 'name',
      role: 'role',
      media: 'image',
    },
    prepare({ name, role, media }) {
      return {
        title: name || 'Person',
        subtitle: role,
        media,
      }
    },
  },
})
