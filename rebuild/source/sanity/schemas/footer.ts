import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'footer',
  title: 'Footer',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: 'Footer Title',
      type: 'string',
      description: 'Internal reference name for this footer',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'columns',
      title: 'Footer Columns',
      type: 'array',
      of: [
        {
          type: 'object',
          name: 'footerColumn',
          title: 'Footer Column',
          fields: [
            {
              name: 'columnTitle',
              title: 'Column Title',
              type: 'string',
              validation: (Rule) => Rule.required(),
            },
            {
              name: 'links',
              title: 'Links',
              type: 'array',
              of: [
                {
                  type: 'object',
                  name: 'footerLink',
                  title: 'Footer Link',
                  fields: [
                    {
                      name: 'label',
                      title: 'Label',
                      type: 'string',
                      validation: (Rule) => Rule.required(),
                    },
                    {
                      name: 'url',
                      title: 'URL',
                      type: 'string',
                      description: 'Internal path or external URL',
                      validation: (Rule) => Rule.required(),
                    },
                    {
                      name: 'openInNewTab',
                      title: 'Open in New Tab',
                      type: 'boolean',
                      initialValue: false,
                    },
                  ],
                  preview: {
                    select: {
                      title: 'label',
                      subtitle: 'url',
                    },
                  },
                },
              ],
            },
          ],
          preview: {
            select: {
              title: 'columnTitle',
              linkCount: 'links',
            },
            prepare({ title, linkCount }) {
              return {
                title,
                subtitle: linkCount ? `${linkCount.length} links` : 'No links',
              }
            },
          },
        },
      ],
    }),
    defineField({
      name: 'socialLinks',
      title: 'Social Links',
      type: 'array',
      of: [
        {
          type: 'object',
          name: 'socialLink',
          title: 'Social Link',
          fields: [
            {
              name: 'platform',
              title: 'Platform',
              type: 'string',
              options: {
                list: [
                  { title: 'Twitter', value: 'twitter' },
                  { title: 'Facebook', value: 'facebook' },
                  { title: 'Instagram', value: 'instagram' },
                  { title: 'LinkedIn', value: 'linkedin' },
                  { title: 'GitHub', value: 'github' },
                  { title: 'YouTube', value: 'youtube' },
                  { title: 'Discord', value: 'discord' },
                  { title: 'TikTok', value: 'tiktok' },
                  { title: 'Other', value: 'other' },
                ],
              },
              validation: (Rule) => Rule.required(),
            },
            {
              name: 'url',
              title: 'URL',
              type: 'url',
              validation: (Rule) => Rule.required().uri({
                scheme: ['http', 'https'],
              }),
            },
            {
              name: 'icon',
              title: 'Icon',
              type: 'string',
              description: 'Custom icon name (if not using platform default)',
            },
          ],
          preview: {
            select: {
              platform: 'platform',
              url: 'url',
            },
            prepare({ platform, url }) {
              return {
                title: platform.charAt(0).toUpperCase() + platform.slice(1),
                subtitle: url,
              }
            },
          },
        },
      ],
    }),
    defineField({
      name: 'bottomText',
      title: 'Bottom Text',
      type: 'object',
      fields: [
        {
          name: 'copyrightText',
          title: 'Copyright Text',
          type: 'string',
          description: 'e.g., © 2024 Company Name. All rights reserved.',
        },
        {
          name: 'additionalLinks',
          title: 'Additional Links',
          type: 'array',
          description: 'Legal links like Privacy Policy, Terms of Service',
          of: [
            {
              type: 'object',
              fields: [
                {
                  name: 'label',
                  title: 'Label',
                  type: 'string',
                  validation: (Rule) => Rule.required(),
                },
                {
                  name: 'url',
                  title: 'URL',
                  type: 'string',
                  validation: (Rule) => Rule.required(),
                },
              ],
              preview: {
                select: {
                  title: 'label',
                  subtitle: 'url',
                },
              },
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
      name: 'newsletter',
      title: 'Newsletter Signup',
      type: 'object',
      fields: [
        {
          name: 'enabled',
          title: 'Enable Newsletter Signup',
          type: 'boolean',
          initialValue: false,
        },
        {
          name: 'title',
          title: 'Title',
          type: 'string',
        },
        {
          name: 'description',
          title: 'Description',
          type: 'text',
          rows: 2,
        },
        {
          name: 'placeholder',
          title: 'Input Placeholder',
          type: 'string',
          initialValue: 'Enter your email',
        },
        {
          name: 'buttonText',
          title: 'Button Text',
          type: 'string',
          initialValue: 'Subscribe',
        },
      ],
      options: {
        collapsible: true,
        collapsed: true,
      },
    }),
  ],
  preview: {
    select: {
      title: 'title',
      columnCount: 'columns',
    },
    prepare({ title, columnCount }) {
      return {
        title,
        subtitle: columnCount ? `${columnCount.length} columns` : 'No columns',
      }
    },
  },
})
