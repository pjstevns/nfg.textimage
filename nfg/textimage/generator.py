# -*- coding: utf-8 -*-

import gd, os
from hashlib import md5

def color2rgb(color):
    assert(color[0]=='#')
    return (int(color[1:3],16),int(color[3:5],16),int(color[5:7],16))

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
        if self.debug: self.force=self.debug=True

        assert(os.path.exists(self.font))

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
            self.file = str(hash.hexdigest()) + '.png'
        self.build_path()

    def init_dimensions(self, w, h):
        if self.width == -1: self.width = w
        if self.height == -1: self.height = h
        minwidth = w+int(self.padding[1])+int(self.padding[3])
        minheight = h+int(self.padding[0])+int(self.padding[2])+(self.size/2)
        self.width=int(max(minwidth,self.width))
        self.height=int(max(minheight,self.height))

    def init_image(self):
        self.image = gd.image((self.width,self.height))
        if self.color[0] != '#': self.color='#000000'
        if self.bgcol[0] != '#': self.bgcol='#ffffff'
        self.color = self.image.colorAllocate(color2rgb(self.color))
        self.bgcol = self.image.colorAllocate(color2rgb(self.bgcol))
        self.image.colorTransparent(self.bgcol)
        self.image.fill((0,0), self.bgcol)

    def get_left(self, linewidth):
        x = 0
        if self.align == 'left': x = int(self.padding[3]);
        elif self.align == 'center': x = (self.width - linewidth)/2
        elif self.align == 'right': x = self.width - linewidth - int(self.padding[1]);
        else: exit(1)
        return int(x)

    def build_path(self):
        self.file = self.file.encode('utf-8')
        assert(len(self.file) > 3)
        for i in range(0,3):
            self.outdir = os.path.join(self.outdir,self.file[i])
            if not os.path.isdir(self.outdir): os.mkdir(self.outdir)
        self.path = os.path.join(self.outdir,self.file)

    def finalize(self):
        f = open(self.path,"w")
        self.image.writePng(f)
        f.close()

    def getPath(self):
        return self.path

class LabelImage(TextImage):

    def __init__(self, **kw):
        TextImage.__init__(self, **kw)
        tim = gd.image((1,1))
        t = tim.get_bounding_rect(self.font, int(self.size), 0.0, (0,int(self.size)), self.text.encode('utf-8'))
        h=t[1]; w=t[4]; 

        self.init_dimensions(w,h)
        self.init_file()

        if not self.force and os.path.exists(self.path): return
                
        self.init_image()

        x = self.get_left(w)
        y = int((self.height + self.size)/2)
        self.image.string_ttf(self.font,int(self.size),0.0,(x,y),self.text.encode('utf-8'),self.color)

        self.finalize()

class PhraseImage(TextImage):

    def __init__(self, **kw):
        TextImage.__init__(self, **kw)

        tim = gd.image((1,1))
##
        words = self.text.split()
        lines = []
        t = tim.get_bounding_rect(self.font, int(self.size), 0.0, (0,int(self.size)), ' ')
        spacew = t[4]; lineh = t[1]

        line = ''
        linew = 0
        maxw = 0
        for word in words:
            wordw = tim.get_bounding_rect(self.font, int(self.size), 0.0, (0, int(self.size)), word.encode('utf-8'))[4]
            if linew + spacew + wordw > self.width:
                lines.append((linew,line))
                maxw = max(linew, maxw)
                line = word
                linew = wordw
            else:
                line = line + ' ' + word
                linew = tim.get_bounding_rect(self.font, int(self.size), 0.0, (0, int(self.size)), line.encode('utf-8'))[4]
        lines.append((linew, line))

        h = len(lines) * lineh
        w = maxw

        self.init_dimensions(w,h)
        self.init_file()

        if not self.force and os.path.exists(self.path): return
                
        self.init_image()

        y = self.padding[0] + lineh
        for (linew,text) in lines:
            x = self.get_left(linew)
            y = int(y)
            self.image.string_ttf(self.font,int(self.size),0.0,(x,y),text.encode('utf-8'),self.color)
            y = y + lineh

        self.finalize()

if __name__ == '__main__':
    print LabelImage(text='Some test',force=True).getPath()
    print LabelImage(text=u'èéëêøæü', force=True,file=u'èéëêøæü.png',color='#00ff00',padding=(5,10,20,30),debug=True).getPath()
    print PhraseImage(text=u'أعلن وزير الخارجية الأمريكي السابق، كولين باول الأحد دعمه للمرشح الديمقراطي، باراك أوباما، مشيراً إلى انزعاجه من حملة المرشح الجمهوري للانتخابات الرئاسية، جون ماكين، في تركيزها على إثارة قضية أن أوباما مسلم.', force=True,file=u'arabic.png',color='#00ff00',padding=(5,10,20,30),debug=True, font='/usr/share/fonts/truetype/ttf-arabeyes/ae_AlMohanad.ttf', align="center").getPath()
