# -*- coding: utf-8 -*-

import gd, os
from md5 import md5

def color2rgb(color):
    assert(color[0]=='#')
    return (int(color[1:3],16),int(color[3:5],16),int(color[5:7],16))

def build_path(outdir, file):
    file = file.encode('utf-8')
    assert(len(file) > 3)
    for i in range(0,3):
        outdir = os.path.join(outdir,file[i])
        if not os.path.isdir(outdir): os.mkdir(outdir)
    return os.path.join(outdir,file)

class LabelImage:

    @staticmethod
    def generate(**kw):
        text='test'
        file=''
        color=(0,0,0)
        bgcol=(255,255,255)
        outdir='/tmp'
        width=-1
        height=-1
        align='left'
        size=12
        font='/usr/share/fonts/truetype/freefont/FreeSans.ttf'
        debug=False
        force=False
        padding=(0,0,0,0)
        if kw.has_key('text'): text=kw['text']
        if kw.has_key('file'): file=kw['file']
        if kw.has_key('color'): color=kw['color']
        if kw.has_key('bgcol'): bgcol=kw['bgcol']
        if kw.has_key('outdir'): outdir=kw['outdir']
        if kw.has_key('width'): width=kw['width']
        if kw.has_key('height'): height=kw['height']
        if kw.has_key('align'): align=kw['align']
        if kw.has_key('size'): size=kw['size']
        if kw.has_key('font') and kw['font']: font=kw['font']
        if kw.has_key('debug'): debug=kw['debug']
        if kw.has_key('force'): force=kw['force']
        if kw.has_key('padding'): padding=kw['padding'] 

        tim = gd.image((1,1))
        if os.path.exists(font):
            t = tim.get_bounding_rect(font, int(size), 0.0, (0,int(size)), text.encode('utf-8'))
        else:
            print "Warning: font file unreadable", font
        h=t[1]; w=t[4]; 

        if width == -1: width = w
        if height == -1: height = h

        minwidth = w+int(padding[1])+int(padding[3])
        minheight = h+int(padding[0])+int(padding[2])+(size/2)
        width=max(minwidth,width)
        height=max(minheight,height)

        if debug: force=debug=True

        # create filename
        if file == '':
            hash = md5()
            hash.update(text.encode('utf-8'))
            hash.update(align)
            hash.update(font)
            hash.update(str(size))
            hash.update(str(color))
            hash.update(str(bgcol))
            hash.update(str(width))
            hash.update(str(height))
            hash.update(str(padding))
            file = str(hash.hexdigest()) + '.png'

        path = build_path(outdir, file)
        if not force and os.path.exists(path): return path
                
        # align text
        x = 0
        if align == 'left': x = int(padding[3]);
        elif align == 'center': x = (width - w)/2
        elif align == 'right': x = width - w - int(padding[1]);
        else: exit(1)

        y = (height + size)/2 
        x = int(x); y = int(y)

        width = int(width)
        height = int(height)

        im = gd.image((width,height))

        if color[0] != '#': color='#000000'
        if bgcol[0] != '#': bgcol='#ffffff'

        color=color2rgb(color)
        bgcol=color2rgb(bgcol)

        color = im.colorAllocate(color)
        bgcol = im.colorAllocate(bgcol)

        im.colorTransparent(bgcol)

        im.fill((0,0), bgcol)
        im.string_ttf(font,int(size),0.0,(x,y),text.encode('utf-8'),color)

        f = open(path,"w")
        im.writePng(f)
        f.close()
        
        return path

class PhraseImage:

    @staticmethod
    def generate(**kw):
        text='test'
        file=''
        color=(0,0,0)
        bgcol=(255,255,255)
        outdir='/tmp'
        width=200
        height=-1
        align='left'
        size=12
        font='/usr/share/fonts/truetype/freefont/FreeSans.ttf'
        debug=False
        force=False
        padding=(0,0,0,0)
        if kw.has_key('text'): text=kw['text']
        if kw.has_key('file'): file=kw['file']
        if kw.has_key('color'): color=kw['color']
        if kw.has_key('bgcol'): bgcol=kw['bgcol']
        if kw.has_key('outdir'): outdir=kw['outdir']
        if kw.has_key('width'): width=kw['width']
        if kw.has_key('height'): height=kw['height']
        if kw.has_key('align'): align=kw['align']
        if kw.has_key('size'): size=kw['size']
        if kw.has_key('font') and kw['font']: font=kw['font']
        if kw.has_key('debug'): debug=kw['debug']
        if kw.has_key('force'): force=kw['force']
        if kw.has_key('padding'): padding=kw['padding'] 

        tim = gd.image((1,1))
##
        words = text.split()
        lines = []
        t = tim.get_bounding_rect(font, int(size), 0.0, (0,int(size)), ' ')
        spacew = t[4]; lineh = t[1]

        line = ''
        linew = 0
        maxw = 0
        for word in words:
            wordw = tim.get_bounding_rect(font, int(size), 0.0, (0, int(size)), word.encode('utf-8'))[4]
            #print "%d,%d %d, %d >>%s<<" %(spacew, spacew*len(word), len(word), int(wordw), word.encode('utf8').strip())
            if linew + spacew + wordw > width:
                lines.append((linew,line))
                maxw = max(linew, maxw)
                line = word
                linew = wordw
            else:
                line = line + ' ' + word
                linew = tim.get_bounding_rect(font, int(size), 0.0, (0, int(size)), line.encode('utf-8'))[4]

        lines.append((linew, line))

        h = len(lines) * lineh
        w = maxw
##
        if width == -1: width = w
        if height == -1: height = h

        minwidth = w+int(padding[1])+int(padding[3])
        minheight = h+int(padding[0])+int(padding[2])+(size/2)
        width=max(minwidth,width)
        height=max(minheight,height)

        if debug: force=debug=True

        # create filename
        if file == '':
            hash = md5()
            hash.update(text.encode('utf-8'))
            hash.update(align)
            hash.update(font)
            hash.update(str(size))
            hash.update(str(color))
            hash.update(str(bgcol))
            hash.update(str(width))
            hash.update(str(height))
            hash.update(str(padding))
            file = str(hash.hexdigest()) + '.png'

        path = build_path(outdir, file)
        if not force and os.path.exists(path): return path
                
        width = int(width)
        height = int(height)

        im = gd.image((width,height))

        if color[0] == '#': color=color2rgb(color)
        if bgcol[0] == '#': bgcol=color2rgb(bgcol)

        color = im.colorAllocate(color)
        bgcol = im.colorAllocate(bgcol)

        im.fill((0,0), bgcol)

        # align text
        y = padding[0] + lineh

        for (linew,text) in lines:
            x = 0
            if align == 'left': x = int(padding[3]);
            elif align == 'center': x = (width - linew)/2
            elif align == 'right': x = width - linew - int(padding[1]);
            else: exit(1)

            x = int(x); y = int(y)
            im.string_ttf(font,int(size),0.0,(x,y),text.encode('utf-8'),color)
            y = y + lineh

        f = open(path,"w")
        im.writePng(f)
        f.close()
        
        return path


if __name__ == '__main__':
    print LabelImage.generate(text='Some test',force=True)
    print LabelImage.generate(text=u'èéëêøæü', force=True,file=u'èéëêøæü.png',color='#00ff00',padding=(5,10,20,30),debug=True)
    print PhraseImage.generate(text=u'أعلن وزير الخارجية الأمريكي السابق، كولين باول الأحد دعمه للمرشح الديمقراطي، باراك أوباما، مشيراً إلى انزعاجه من حملة المرشح الجمهوري للانتخابات الرئاسية، جون ماكين، في تركيزها على إثارة قضية أن أوباما مسلم.', force=True,file=u'arabic.png',color='#00ff00',padding=(5,10,20,30),debug=True, font='/usr/share/fonts/truetype/ttf-arabeyes/ae_AlMohanad.ttf', align="center")
