"""
Image Tag
---------
This implements a Liquid-style image tag for Pelican,
based on the octopress image tag [1]_

Syntax
------
{% img [class name(s)] [http[s]:/]/path/to/image [width [height]] [title text | "title text" ["alt text"]] %}

Altered tag:
In following formats, will generate figures:
    ... "Title" "Alt" "Source" %}   <- figure with Title, alt=Alt and appended "(source)" as  a hyperlink to caption
    ... "" "Alt" %}                 <- figure with no caption but alt
    ... "Title" "" %}               <- figure with caption and alt=Title

Examples
--------
{% img /images/ninja.png Ninja Attack! %}
{% img left half http://site.com/images/ninja.png Ninja Attack! %}
{% img left half http://site.com/images/ninja.png 150 150 "Ninja Attack!" "Ninja in attack posture" %}

Output
------
<img src="/images/ninja.png">
<img class="left half" src="http://site.com/images/ninja.png" title="Ninja Attack!" alt="Ninja Attack!">
<img class="left half" src="http://site.com/images/ninja.png" width="150" height="150" title="Ninja Attack!" alt="Ninja in attack posture">

[1] https://github.com/imathis/octopress/blob/master/plugins/image_tag.rb
"""
import re

import six

from .mdx_liquid_tags import LiquidTags

SYNTAX = '{% img [class name(s)] [http[s]:/]/path/to/image [width [height]] [title text | "title text" ["alt text"]] %}'

# Regular expression to match the entire syntax
ReImg = re.compile(
    r"""(?P<class>\S*\s)?(?P<src>(?:https?:\/\/|\/|\S+\/)\S+)(?:\s+(?P<width>\d+))?(?:\s+(?P<height>\d+))?(?P<title>\s+.+)?"""
)

# Regular expression to split the title and alt text
ReTitleAltSource = re.compile(
    r"""(?:"|')(?P<title>[^"']+)?(?:"|')\s+(?:"|')(?P<alt>[^"']+)?(?:"|')\s+(?:"|')(?P<source>[^"']+)?(?:"|')""")
ReTitleAlt = re.compile(
    r"""(?:"|')(?P<title>[^"']+)?(?:"|')\s+(?:"|')(?P<alt>[^"']+)?(?:"|')"""
)


@LiquidTags.register("img")
def img(preprocessor, tag, markup):
    attrs = None
    source_tag = None

    # Parse the markup string
    match = ReImg.search(markup)
    if match:
        attrs = dict(
            [
                (key, val.strip())
                for (key, val) in six.iteritems(match.groupdict())
                if val
            ]
        )
    else:
        raise ValueError(
            "Error processing input. " "Expected syntax: {0}".format(SYNTAX)
        )

    # See if source exists (must provide all 3 title/alt/source)
    # Check if alt text or source are present -- if so, split it from title
    if 'title' in attrs:
        match = ReTitleAltSource.search(attrs['title'])
        if match: # set title, alt, leave source
            attrs['title'] = match.groupdict()['title']
            attrs['alt'] = match.groupdict()['alt']
            source_tag = match.groupdict()['source']
        else:
            match = ReTitleAlt.search(attrs['title']) # if no source, get title/alt
            if match:
                attrs.update(match.groupdict())
            if (not attrs.get('alt')) or attrs['alt'] == "":
                attrs['alt'] = attrs['title'] # no alt, set to title

    tag_out = "<figure>"
    fig_tag = ""

    # Return the formatted text

    if attrs['title'] is not None: # special case: sets title=alt but no caption
        fig_tag = "<figcaption>" + attrs['title']
    else:
        attrs['title'] = attrs['alt'] # if no title, add as alt in image

    if 'class' in attrs: # set figure class if given
        tag_out = '<figure class="' + attrs['class'] + '">'
    
    # add all arguments
    tag_out = tag_out + "<img {0}>".format(' '.join('{0}="{1}"'.format(key, val)
                                       for (key, val) in six.iteritems(attrs)))
    tag_out = tag_out + fig_tag
    
    # if source, append to caption
    if source_tag:
        tag_out = tag_out + " (<a href='" + source_tag + "'>source</a>)"
    
    if fig_tag != "": # close tag if caption present
        tag_out = tag_out + "</figcaption></figure>"
    else:
        tag_out = tag_out + "</figure>"

    return tag_out


# ----------------------------------------------------------------------
# This import allows image tag to be a Pelican plugin
from .liquid_tags import register  # noqa
