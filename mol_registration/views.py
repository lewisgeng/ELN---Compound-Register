from django.http import HttpResponse
from django.shortcuts import render, redirect
from rdkit import Chem
from rdkit.Chem import AllChem,Descriptors,Draw
from .models import mol_props

# Create your views here.
def registration(request):
    if request.method == 'POST':
        if request.POST.get('getsmiles') != '':
            #分子属性及ID
            smiles = request.POST.get('getsmiles')
            mol = Chem.MolFromSmiles(smiles)
            tpsa = round(Descriptors.TPSA(mol),3)
            logp = round(Descriptors.MolLogP(mol),3)
            mw = round(Descriptors.MolWt(mol),3)
            compound_id_last = mol_props.objects.order_by('-compound_id').first().compound_id
            #print(compound_id_last)
            id = compound_id_last.split('-')[1]
            id_1 = int(id)+1
            id_2 = str(id_1).zfill(6)
            compound_id = 'QL-' + id_2
            #分子图片输出
            Draw.MolToFile(mol, './register/template/static/mol_image/%s.png' % compound_id)
            img_path = '/static/mol_image/%s.png' % compound_id
            #render进html页面
            ctx = {}
            ctx['tpsa'] = tpsa
            ctx['logp'] = logp
            ctx['mw'] = mw
            ctx['compound_id'] = compound_id
            ctx['img_path'] = img_path
            ctx['smiles'] = smiles
            return render(request,'registration.html',locals())
        else:
            return redirect("/index/")

def reg_result(request):
    if request.method == 'POST':
        smiles = request.POST.get('smiles')
        logp = request.POST.get('logp')
        mw = request.POST.get('mw')
        compound_id = request.POST.get('compound_id')
        img_path = request.POST.get('img_path')
        tpsa = request.POST.get('tpsa')
        #print(smiles,logp,compound_id)
        if mol_props.objects.filter(smiles=smiles).exists():
            return HttpResponse('化合物已存在，请勿重复注册！')
        else:
            molecule_insert = mol_props.objects.create(compound_id=compound_id, smiles=smiles, TPSA=tpsa, xlogp=logp, MW=mw, img_file=img_path)
            molecule_insert.save()
            return HttpResponse('化合物注册成功！')