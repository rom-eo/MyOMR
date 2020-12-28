'''
MyOmr module
Requires:
pdf2image, numpy, PIL
'''

import numpy as np
from PIL import Image,ImageOps 

def subIm(image,i,j,nx,ny):
    '''
    return a cropted image
    nx,ny: step size or rectangle length
    '''
    x,y=image.size
    rec=(i*x//nx,j*y//ny,
         (i+1)*x//nx,(1+j)*y//ny)
    # crop and convert to black white
    return image.crop(box=rec).convert('L')

def recToBit(img):
    alpha=2
    A=img.histogram()
    return [0,1][sum(A[:128]) > alpha*sum(A[128:])]

def model2():
    """ 
    Returns a dictionary d.
    The model comsists of subdividing the
    image into 20 rows and 20 columns.
    The dictionary gives the position of 
    the input fields. 
    Keys are: 
    ID1, ..., ID15
    A1, ..., A24
    ...
    E1, ..., E24.
    d[key] is the position as row and column.
    Row:0 is up and 20 is botom.
    Column:0 is left and 20 is right.
    """
    lettr="ABCDE"
    id= {'ID'+str(i+1):(3+i,2) for i in range(15)}
    rep1={lettr[j]+str(i+1):(3+j,6+i) for i in range(12) for j in range(5)}
    rep2={lettr[j]+str(13+i):(13+j,6+i) for i in range(12) for j in range(5)}
    d={}
    for dd in [id,rep1,rep2]:
        d.update(dd)
    return d   


def fields(imagePath,aModel):
    """
    aModel: a dictionary giving the position 
    of the input fields.
    Returns a dict with arrays representing 
    images for each field.    
    """
    img = Image.open(imagePath) 
    res={}
    for key,value in aModel.items():
        i=value[0]
        j=value[1]
        res[key]=subIm(img,i,j,20,20)
    return res

def digital_read(aDict):
    """
    aDict: key is a field name (str)
    value is a np.array representing the image
    """
    lim=[100,175]
    res={}
    for key,value in aDict.items():
        print(value.shape)
        test=value.mean()
        if test<lim[0]:
            res[key]=0
        elif test>lim[1]:
            res[key]=1
        else:
            res[key]=-1
    return res

def grade(aModel,testImg,solImg,partial='no'):
    '''
    Options for partial are 'no' and 'yes'.
    Only no is implemented for now.
    '''
    A=[]
    if partial=='no':
        aModel=model2()
        zTest=readIm(testImg,aModel)
        zSol=readIm(solImg,aModel)
        
        
        score=0
        total=0
        # questions
        for i in range(24):
            aList=[a+str(i+1) for a in 'ABCDE' ]
            valSol=[zSol[key] for key in aList]
            valTest=[zTest[key] for key in aList]
            if 1 in valSol:
                total+=1
                if valSol==valTest:
                    score+=1
        # ID 
        idList= ['ID'+str(i+1) for i  in range(15) ]       
        idnum=[zTest[key] for key in idList]
        #idnum=bitsToDec(idnum)
    return idnum,score,total

def grade_binary(aModel,testImg,solImg):
    resTest=digital_read(fields(testImg,aModel))
    resSol=digital_read(fields(solImg,aModel))
    score=0
    total=0
    # generalize
    for i in range(24):
        aList=[a+str(i+1) for a in 'ABCDE' ]
        valSol=[resSol[key] for key in aList]
        valTest=[resTest[key] for key in aList]
        if 1 in valSol:
            total+=1
            if valSol==valTest:
                score+=1
    # generalize
    idList= ['ID'+str(i+1) for i  in range(15) ]       
    idnum=[resTest[key] for key in idList]
    idnum=bitsToDec(idnum)
    return idnum,score,total

def bitsToDec(a):
    """
    a is a list of bits (0,1).
    Return a decimal,
    """
    b=list(a)
    b.reverse()
    #print('b=',b)
    val=b[0]
    expo=1
    for index,value in enumerate(b[1:]):
        expo*=2
        val+=expo*value
    return val
        
            
        
            
   
def image_to_black_white(img):
    """
    img: a PIL image
    """
    limit = 200
    function = lambda x : [0,255][ x >limit]
    return img.convert('L').point(function, mode='1')
    
def readIm(imPath,aModel):
    z=fields(imPath,aModel)
    A={}
    for key in aModel.keys():
        A[key]=recToBit( z[key])
    return A
    

def example():
    
    aModel=model2()
    testImg="test.jpeg"
    solImg="sol.jpeg"
        
    res=grade(aModel,testImg,solImg)
    print(res)   

def example2():
    
    aModel=model2()
    testImg="test.jpeg"
    solImg="sol.jpeg"
    '''
    zTest=readIm(testImg,aModel)
    zSol=readIm(solImg,aModel)
    
    A=[]
    
    for key in aModel.keys():
        if zTest[key]!=zSol[key] and not key.startswith('ID'):
            A.append(key)
            
    return A       
    '''    
    res=grade_binary(aModel,testImg,solImg)
    print(res)

def intToBase58(anInt):
    Base58='123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
    res=[]
    while anInt>=58:
        res.append(anInt%58)
        anInt=anInt//58
    res.append(anInt)
    res=[Base58[a] for a in res]
    return "".join(res)


def pdfToimage(filePath,imFormat='JPEG',output=""):
    """
    A wrapper on pdf2image
    """
    from pdf2image import convert_from_path 
    images = convert_from_path(filePath) 
    
    for index,img in enumerate(images):
        if output=="":
            output=filePath+f'_{index}'
        img.save(output+f'.{imFormat.lower()}', imFormat)

   
def gen_rand_pdf(aModel):
    """
    Generate a random pdf

    """
    import random
    import subprocess
    choice={}
    text=[]
    for key,value in aModel.items():
        choice[key]=random.choice([0,1])
        
        x=value[0]
        y=value[1]
        if choice[key]==1:
            temp=rf'\draw[fill] ({(y)/20},{(20-x)/20}) rectangle ({(y+1)/20},{(20-x-1)/20});'
            text.append(temp)
    text="\n".join(text)
    #print(text)
    textTex=open('trial_cases.tex','r')
    textTex=textTex.read()
    text1,text2=textTex.split(r'%inserthereOK')
    text="\n".join([text1,text,text2])
    name=sorted(choice.items())
    name=[a[1] for a in name]
    fileName=intToBase58(bitsToDec(name))
    f=open(fileName+'.tex','w')
    f.write(text)
    f.close()
    command=['pdflatex',fileName]
    res = subprocess.run(command,capture_output=True)
    res = subprocess.run(command,capture_output=True)
    
    
    
    
  
