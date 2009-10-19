# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import os
from hashlib import md5

class TextImage:

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
    type="gif"
    padding=(0,0,0,0)

    def __init__(self, **kw):
        if kw.has_key('text'): self.text=kw['text']
        if kw.has_key('file'): self.file=kw['file']
        if kw.has_key('color'): self.color=kw['color']
        if kw.has_key('bgcol'): self.bgcol=kw['bgcol']
        if kw.has_key('outdir'): self.outdir=kw['outdir']
        if kw.has_key('width'): self.width=kw['width']
        if kw.has_key('height'): self.height=kw['height']
        if kw.has_key('align'): self.align=kw['align']
        if kw.has_key('size'): self.size=kw['size']
        if kw.has_key('font') and kw['font']: self.font=kw['font']
        if kw.has_key('debug'): self.debug=kw['debug']
        if kw.has_key('force'): self.force=kw['force']
        if kw.has_key('padding'): self.padding=kw['padding'] 
        if kw.has_key('type'): self.type=kw['type'].lower()
        if self.debug: self.force=self.debug=True

        assert(os.path.exists(self.font))
        assert(self.type in ('gif','png'))
        self._font = ImageFont.truetype(self.font, int(self.size))

    def init_file(self):
        # create filename
        if self.file == '':
            hash = md5()
            hash.update(self.text.encode('utf-8'))
            hash.update(self.align)
            hash.update(self.font)
            hash.update(str(self.size))
            hash.update(str(self.color))
            hash.update(str(self.bgcol))
            hash.update(str(self.width))
            hash.update(str(self.height))
            hash.update(str(self.padding))
            self.file = str(hash.hexdigest()) + '.%s' % self.type
        self.build_path()

    def init_dimensions(self, w, h):
        if self.width == -1: self.width = w
        if self.height == -1: self.height = h
        minwidth = w+int(self.padding[1])+int(self.padding[3])
        minheight = h+int(self.padding[0])+int(self.padding[2])+(self.size/2)
        self.width=int(max(minwidth,self.width))
        self.height=int(max(minheight,self.height))

    def init_image(self):
        if self.color[0] != '#': self.color='#000000'
        if self.bgcol[0] != '#': self.bgcol='#ffffff'
        self.image = Image.new(mode='RGBA', size=(self.width, self.height), color=self.bgcol)
        self.image.info['quality'] = 100

    def get_left(self, linewidth):
        x = 0
        if self.align == 'left': x = int(self.padding[3]);
        elif self.align == 'center': x = (self.width - linewidth)/2
        elif self.align == 'right': x = self.width - linewidth - int(self.padding[1]);
        else: exit(1)
        return int(x)

    def build_path(self):
        assert(len(self.file) > 3)
        for i in range(0,3):
            self.outdir = os.path.join(self.outdir,self.file[i].encode('utf-8'))
            if not os.path.isdir(self.outdir): os.mkdir(self.outdir)
        self.path = os.path.join(self.outdir,self.file.encode('utf-8'))

    def finalize(self):
        if self.type=='gif':
            self.image = self.image.convert('RGB').convert('P', palette=Image.ADAPTIVE)
        self.image.save(self.path, self.type.upper(), quality=100)

    def getPath(self):
        return self.path

class LabelImage(TextImage):

    def __init__(self, **kw):
        TextImage.__init__(self, **kw)
        w,h = self._font.getsize(self.text.encode('utf-8'))

        self.init_dimensions(w,h)
        self.init_file()

        if not self.force and os.path.exists(self.path): return
                
        self.init_image()

        x = self.get_left(w)
        y = int(self.padding[0]) + ((self.height - int(self.padding[0]) - h - int(self.padding[2])) / 2)
        d = ImageDraw.Draw(self.image)
        d.text((x,y),self.text, font=self._font, fill=self.color)
        del(d)
        self.finalize()

class PhraseImage(TextImage):

    def __init__(self, **kw):
        TextImage.__init__(self, **kw)
##
        words = self.text.split()
        lines = []
        spacew, lineh = self._font.getsize(u' ')

        line = ''
        linew = 0
        maxw = 0
        for word in words:
            wordw = self._font.getsize(word.encode('utf-8'))[0]
            if linew + spacew + wordw > self.width:
                lines.append((linew,line))
                maxw = max(linew, maxw)
                line = word
                linew = wordw
            else:
                line = line + ' ' + word
                linew = self._font.getsize(line.encode('utf-8'))[0]
        lines.append((linew, line))

        h = len(lines) * lineh
        w = maxw

        self.init_dimensions(w,h)
        self.init_file()

        if not self.force and os.path.exists(self.path): return
                
        self.init_image()

        y = self.padding[0]
        d = ImageDraw.Draw(self.image)
        for (linew,text) in lines:
            x = self.get_left(linew)
            y = int(y)
            d.text((x,y), text, font=self._font, fill=self.color)
            y = y + lineh
        del(d)

        self.finalize()

if __name__ == '__main__':
    print LabelImage(text='Some test',force=True).getPath()
    print LabelImage(text=u'èéëêøæü', force=True,file=u'èéëêøæü.gif',color='#00ff00',padding=(5,10,20,30),debug=True).getPath()
    print PhraseImage(text=u'أعلن وزير الخارجية الأمريكي السابق، كولين باول الأحد دعمه للمرشح الديمقراطي، باراك أوباما، مشيراً إلى انزعاجه من حملة المرشح الجمهوري للانتخابات الرئاسية، جون ماكين، في تركيزها على إثارة قضية أن أوباما مسلم.', force=True,file=u'arabic.gif',color='#00ff00',width=800, height=500, padding=(5,10,20,30),debug=True, font='/usr/share/fonts/truetype/ttf-arabeyes/ae_AlMohanad.ttf', align="center").getPath()
    print PhraseImage(text=u'Vestibulum et ullamcorper nunc. Nullam vitae eleifend nibh. Aliquam pellentesque pellentesque eros vel vehicula. Nam accumsan magna at nisi hendrerit scelerisque. Ut quis quam nulla, in tempor urna. Proin non ornare enim. Morbi tellus lectus, accumsan vitae viverra non, ornare et libero.', force=True,file=u'ipsum.gif',color='#00ff00',width=800, height=500, padding=(5,10,20,30),debug=True, align="center").getPath()
