import operator

from django.http import HttpResponse
from django.shortcuts import render, redirect
from rdkit import Chem,DataStructs
from rdkit.Chem import AllChem,Descriptors,Draw
from .models import mol_props

# Create your views here.
def registration(request):
    if request.method == 'POST':
        if request.POST.get('getsmiles') != '':
            #分子属性及ID
            smiles = request.POST.get('getsmiles')
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                tpsa = round(Descriptors.TPSA(mol),3)
                logp = round(Descriptors.MolLogP(mol),3)
                mw = round(Descriptors.MolWt(mol),3)
                if mol_props.objects.all().count() != 0:
                    compound_id_last = mol_props.objects.order_by('-compound_id').first().compound_id
                    #print(compound_id_last)
                    id = compound_id_last.split('-')[1]
                    id_1 = int(id)+1
                    id_2 = str(id_1).zfill(6)
                    compound_id = 'QL-' + id_2
                    # 分子图片输出
                    Draw.MolToFile(mol, './register/template/static/mol_image/%s.png' % compound_id)
                    img_path = '/static/mol_image/%s.png' % compound_id
                else:
                    compound_id = 'QL-000001'
                    # 分子图片输出
                    Draw.MolToFile(mol, './register/template/static/mol_image/%s.png' % compound_id)
                    img_path = '/static/mol_image/%s.png' % compound_id
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
                return HttpResponse('化合物结构错误，请重新输入！')
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
        mol_mem = Chem.MolFromSmiles(smiles)
        mol = Chem.MolToMolBlock(mol_mem)
        mol_file_tmp = open('./register/template/static/mol_file/%s.mol' % compound_id,'w')
        mol_file_tmp.write(mol)
        mol_file_tmp.close()
        mol_file_path = '/static/mol_file/%s.mol' % compound_id
        #print(mol)
        fp = AllChem.GetMorganFingerprintAsBitVect(mol_mem, radius=2).ToBitString()
        #print(fp)
        if mol_props.objects.filter(smiles=smiles).exists():
            return HttpResponse('化合物已存在，请勿重复注册！')
        else:
            molecule_insert = mol_props.objects.create(compound_id=compound_id, smiles=smiles, mol_file=mol, TPSA=tpsa, xlogp=logp, MW=mw, img_file=img_path,fingerprint=fp, mol_file_path=mol_file_path)
            molecule_insert.save()
            return HttpResponse('化合物注册成功！')

def search(request):
    if request.method == 'POST':
        if request.POST.get('getsearchsmiles') != '' and request.POST.get('similarity') !='':
            getsearchsmiles = request.POST.get('getsearchsmiles')
            getsimilarity = float(request.POST.get('similarity'))
            getsearchmol = Chem.MolFromSmiles(getsearchsmiles)
            getsearchmol_fp = Chem.AllChem.GetMorganFingerprint(getsearchmol,2)
            if getsearchmol:
                mol_list = mol_props.objects.all()
                search_result = []
                for item in mol_list:
                    search_dict = {}
                    smiles = item.smiles
                    mol = Chem.MolFromSmiles(smiles)
                    fp = Chem.AllChem.GetMorganFingerprint(mol,2)
                    similarity =DataStructs.DiceSimilarity(fp,getsearchmol_fp)
                    if similarity > getsimilarity:
                        search_dict['compound_id'] = item.compound_id
                        search_dict['img_file'] = item.img_file
                        search_dict['smiles'] = item.smiles
                        search_dict['mol_file_path'] = item.mol_file_path
                        search_dict['similarity'] = round(similarity,3)
                        search_result.append(search_dict)
                search_result_sorted = sorted(search_result,key=operator.itemgetter('similarity'),reverse=True)
                print(search_result_sorted)
                return render(request,'search.html',{'search_result':search_result_sorted})
        else:
            return HttpResponse('请输入结构和相似性数值！')


