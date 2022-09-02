import operator
import os
import time
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rdkit import Chem, DataStructs
import rdkit
from rdkit.Chem import AllChem, Descriptors
from rdkit.Chem.Draw import rdMolDraw2D
from .models import mol_props
from . import models
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


# Create your views here.
def registration(request):
    if request.method == 'POST':
        if request.POST.get('getsmiles') != '':
            #分子属性及ID
            smiles_original = request.POST.get('getsmiles')
            print(smiles_original)

            mol_check = Chem.MolFromSmiles(smiles_original)
            if mol_check is None:
                html = '<center><p>化合物结构错误，请重新输入！</p></br><a href = \'/index/\'>返回首页</a></center>'
                return HttpResponse(html)
            else:
                # convert to canonsmiles
                smiles = rdkit.Chem.CanonSmiles(smiles_original)
                print(smiles)
                mol = Chem.MolFromSmiles(smiles)
                #print(smiles)
                tpsa = round(Descriptors.TPSA(mol), 3)
                logp = round(Descriptors.MolLogP(mol), 3)
                mw = round(Descriptors.MolWt(mol), 3)
                if mol_props.objects.all().count() != 0:
                    compound_id_last = mol_props.objects.order_by('-compound_id').first().compound_id
                    #print(compound_id_last)
                    id = compound_id_last.split('-')[1]
                    id_1 = int(id)+1
                    id_2 = str(id_1).zfill(6)
                    compound_id = 'QL-' + id_2
                    # 分子图片输出
                    d = rdMolDraw2D.MolDraw2DCairo(300, 300)
                    d.DrawMolecule(mol)
                    d.FinishDrawing()
                    d.WriteDrawingText('./register/template/static/mol_image/%s.png' % compound_id)
                    img_path = '/static/mol_image/%s.png' % compound_id
                else:
                    compound_id = 'QL-000001'
                    # 分子图片输出
                    d = rdMolDraw2D.MolDraw2DCairo(300, 300)
                    d.DrawMolecule(mol)
                    d.FinishDrawing()
                    d.WriteDrawingText('./register/template/static/mol_image/%s.png' % compound_id)
                    img_path = '/static/mol_image/%s.png' % compound_id
                ctx = {}
                ctx['tpsa'] = tpsa
                ctx['logp'] = logp
                ctx['mw'] = mw
                ctx['compound_id'] = compound_id
                ctx['img_path'] = img_path
                ctx['smiles'] = smiles
                return render(request, 'registration.html', locals())
        else:
            return redirect("/index/")


def reg_result(request):
    if request.method == 'POST':
        smiles_original = request.POST.get('smiles')
        logp = request.POST.get('logp')
        mw = request.POST.get('mw')
        compound_id = request.POST.get('compound_id')
        img_path = request.POST.get('img_path')
        tpsa = request.POST.get('tpsa')
        #convert to canonsmiles
        smiles = rdkit.Chem.CanonSmiles(smiles_original)
        mol_mem = Chem.MolFromSmiles(smiles)
        mol = Chem.MolToMolBlock(mol_mem)
        mol_file_tmp = open('./register/template/static/mol_file/%s.mol' % compound_id, 'w')
        mol_file_tmp.write(mol)
        mol_file_tmp.close()
        mol_file_path = '/static/mol_file/%s.mol' % compound_id
        #print(mol)
        fp = AllChem.GetMorganFingerprintAsBitVect(mol_mem, radius=2).ToBitString()
        #print(fp)
        if mol_props.objects.filter(smiles=smiles).exists():
            html = '<center><p>化合物已存在，请勿重复注册！</p></br><a href = \'/index/\'>返回首页</a></center>'
            return HttpResponse(html)
        else:
            molecule_insert = mol_props.objects.create(compound_id=compound_id, smiles=smiles, mol_file=mol, TPSA=tpsa, xlogp=logp, MW=mw, img_file=img_path, fingerprint=fp, mol_file_path=mol_file_path)
            molecule_insert.save()
            html = '<center><p>化合物注册成功！</p></br><a href = \'/compoundlist/\'>Compound List</a></center>'
            return HttpResponse(html)


def delete_compound(request):
    if request.session.get('is_login'):
        delete_compound_id = request.GET.get('delete_compound_id')
        username = request.session['username']
        if mol_props.objects.filter(compound_id=delete_compound_id).exists():
            edit_compound_item = mol_props.objects.get(compound_id=delete_compound_id)
            image_path = edit_compound_item.img_file
        return render(request, "confirm_delete_compound.html", {"delete_compound_id": delete_compound_id,'username':username,'image_path':image_path})
    else:
        return redirect('/login/')


def confirm_delete_compound(request):
    if request.session.get('is_login'):
        delete_compound_id = request.GET.get('delete_compound_id')
        confirm_or_not = request.GET.get('confirm_delete')
        if delete_compound_id and confirm_or_not == '1':
            models.mol_props.objects.filter(compound_id=delete_compound_id).delete()
            mol_file_path = './register/template/static/mol_file/%s.mol' % delete_compound_id
            mol_img_path = './register/template/static/mol_image/%s.png' % delete_compound_id
            if os.path.exists(mol_file_path):
                os.remove(mol_file_path)
            if os.path.exists(mol_img_path):
                os.remove(mol_img_path)
            html = '<center><p>删除成功！</p></br><a href = \'/compoundlist/\'>返回</a></center>'
            return HttpResponse(html)
        else:
            return redirect('/compoundlist/')


def edit_compound(request):
    if request.session.get('is_login'):
        username = request.session['username']
        if request.method == 'GET':
            edit_compound_id = request.GET.get('edit_compound_id')
            #return HttpResponse("开始edit")
            #print(edit_compound_id)
            if mol_props.objects.filter(compound_id=edit_compound_id).exists():
                edit_compound_item = mol_props.objects.get(compound_id=edit_compound_id)
            ctx={}
            ctx['edit_compound_item_smiles'] = edit_compound_item.smiles
            ctx['edit_compound_item_compound_id'] = edit_compound_item.compound_id
            ctx['username'] = username
            return render(request, "edit_compound.html", ctx)
        elif request.method == 'POST':
            #update_edit_smiles = request.POST.get('update_edit_smiles')
            update_origin_compound_id = request.POST.get('edit_compound_item_compound_id')
            if models.mol_props.objects.filter(compound_id=update_origin_compound_id).exists():
                update_item = mol_props.objects.get(compound_id=update_origin_compound_id)
                update_edit_smiles = request.POST.get('update_edit_smiles')
                #print(update_edit_smiles)
                mol_check = Chem.MolFromSmiles(update_edit_smiles)
                if mol_check is None:
                    html = '<center><p>结构有误，请重新输入！</p></br><a href = \'http://localhost:8000/edit_compound/?edit_compound_id=%s\'>返回</a></center>' % update_origin_compound_id
                    return HttpResponse(html)
                else:
                    if rdkit.Chem.CanonSmiles(update_edit_smiles, useChiral=1) == rdkit.Chem.CanonSmiles(
                            update_item.smiles, useChiral=1):
                        html = '<center><p>结构未做任何修改！</p></br><a href = \'http://localhost:8000/edit_compound/?edit_compound_id=%s\'>返回</a></center>' % update_origin_compound_id
                        return HttpResponse(html)
                    models.mol_props.objects.filter(compound_id=update_origin_compound_id).delete()
                    mol_file_path = './register/template/static/mol_file/%s.mol' % update_origin_compound_id
                    mol_img_path = './register/template/static/mol_image/%s.png' % update_origin_compound_id
                    if os.path.exists(mol_file_path):
                        os.remove(mol_file_path)
                    if os.path.exists(mol_img_path):
                        os.remove(mol_img_path)
                    smiles = rdkit.Chem.CanonSmiles(update_edit_smiles, useChiral=1)
                    mol_mem = Chem.MolFromSmiles(smiles)
                    tpsa = round(Descriptors.TPSA(mol_mem), 3)
                    logp = round(Descriptors.MolLogP(mol_mem), 3)
                    mw = round(Descriptors.MolWt(mol_mem), 3)
                    mol = Chem.MolToMolBlock(mol_mem)
                    mol_file_tmp = open('./register/template/static/mol_file/%s.mol' % update_origin_compound_id, 'w')
                    mol_file_tmp.write(mol)
                    mol_file_tmp.close()
                    mol_file_path = '/static/mol_file/%s.mol' % update_origin_compound_id
                    d = rdMolDraw2D.MolDraw2DCairo(300, 300)
                    d.DrawMolecule(mol_mem)
                    d.FinishDrawing()
                    d.WriteDrawingText('./register/template/static/mol_image/%s.png' % update_origin_compound_id)
                    img_path = '/static/mol_image/%s.png' % update_origin_compound_id
                    time.sleep(0.25)
                    # print(mol)
                    fp = AllChem.GetMorganFingerprintAsBitVect(mol_mem, radius=2).ToBitString()
                    # print(fp)
                    if mol_props.objects.filter(smiles=smiles).exists():
                        html = '<center><p>化合物已存在！</p></br><a href = \'http://localhost:8000/edit_compound/?edit_compound_id=%s\'>返回</a></center>' % update_origin_compound_id
                        return HttpResponse(html)
                    else:
                        molecule_insert = mol_props.objects.create(compound_id=update_origin_compound_id, smiles=smiles, mol_file=mol,
                                                                   TPSA=tpsa, xlogp=logp, MW=mw, img_file=img_path,
                                                                   fingerprint=fp, mol_file_path=mol_file_path)
                        molecule_insert.save()
                        time.sleep(0.25)
                        return redirect("/compoundlist/")
    else:
        return redirect("/login/")


def compoundlist(request):
    if request.session.get('is_login'):
        mol_list = mol_props.objects.all().order_by('-compound_id')
        paginator = Paginator(mol_list, 10)
        page = request.GET.get('page', 1)
        #print(page)
        username = request.session['username']
        try:
            sublist = paginator.page(page)
        except PageNotAnInteger:
            sublist = paginator.page(1)
        except EmptyPage:
            sublist = paginator.page(paginator.num_pages)
        return render(request, "compoundlist.html", {"sublist": sublist, 'username': username})
    else:
        return redirect("/login/")

def search(request):
    if request.session.get('is_login'):
        ctx={}
        ctx['aa'] = '这是search页面'
        ctx['username'] = request.session['username']
        return render(request, "search.html",ctx)
    else:
        return redirect('/login/')


def search_result(request):
    if request.session.get('is_login'):
        ##相似性结构检索，输入Similarity数值以及不输入Similarity数值
        if request.POST.get('getsearchsmiles') != '' and request.POST.get('similarity') != '':
            getsearchsmiles = rdkit.Chem.CanonSmiles(request.POST.get('getsearchsmiles'), useChiral=1)
            getsimilarity = float(request.POST.get('similarity'))
            getsearchmol = Chem.MolFromSmiles(getsearchsmiles)
            getsearchmol_fp = Chem.AllChem.GetMorganFingerprint(getsearchmol, 2)
            if getsearchmol:
                mol_list = mol_props.objects.all()
                search_result = []
                for item in mol_list:
                    search_dict = {}
                    smiles = item.smiles
                    mol = Chem.MolFromSmiles(smiles)
                    fp = Chem.AllChem.GetMorganFingerprint(mol, 2)
                    similarity = DataStructs.DiceSimilarity(fp, getsearchmol_fp)
                    if similarity > getsimilarity:
                        search_dict['compound_id'] = item.compound_id
                        search_dict['img_file'] = item.img_file
                        search_dict['smiles'] = item.smiles
                        search_dict['mol_file_path'] = item.mol_file_path
                        search_dict['MW'] = item.MW
                        search_dict['TPSA'] = item.TPSA
                        search_dict['similarity'] = round(similarity, 3)
                        search_dict['xlogp'] = round(item.xlogp, 3)
                        search_result.append(search_dict)
                search_result_sorted = sorted(search_result, key=operator.itemgetter('similarity'), reverse=True)
                username = request.session['username']
                return render(request, 'search_result.html', {'search_result_sorted': search_result_sorted,'username':username})
        if request.POST.get('getsearchsmiles') != '' and request.POST.get('similarity') == '':
            html = '<center><p>请输入相似性数值！</p></br><a href = \'/search/\'>返回搜索页面</a></center>'
            return HttpResponse(html)

        ##属性检索Compound ID
        if request.POST.get('compound_id') != '' and request.POST.get('similarity'):
            compound_id = request.POST.get('compound_id')
            mol_list = mol_props.objects.all()
            search_result = []
            for mol in mol_list:
                search_dict = {}
                if compound_id.upper() in mol.compound_id.upper():
                    search_dict['compound_id'] = mol.compound_id
                    search_dict['img_file'] = mol.img_file
                    search_dict['smiles'] = mol.smiles
                    search_dict['MW'] = mol.MW
                    search_dict['mol_file_path'] = mol.mol_file_path
                    search_dict['similarity'] = 'N/A'
                    search_dict['TPSA'] = mol.TPSA
                    search_dict['xlogp'] = round(mol.xlogp, 3)
                    search_result.append(search_dict)
                #else:
                 #   return HttpResponse('没有检索到包含此ID的化合物！')
            if len(search_result) == 0:
                html = '<center><p>没有检索到包含此ID的化合物！</p></br><a href = \'/search/\'>返回搜索页面</a></center>'
                return HttpResponse(html)
            else:
                username = request.session['username']
                search_result_sorted = sorted(search_result, key=operator.itemgetter('compound_id'), reverse=False)
            return render(request, 'search_result.html', {'search_result_sorted': search_result_sorted,'username':username})

        ##属性检索MW
        if request.POST.get('mw_value') and request.POST.get('mw_qualifier') and request.POST.get('similarity') :
            mw_value = float(request.POST.get('mw_value'))
            qf = request.POST.get('mw_qualifier')
            #print(qf)
            mol_list = mol_props.objects.all()
            search_result = []
            if qf == '<':
                for mol in mol_list:
                    search_dict = {}
                    if mol.MW < mw_value:
                        search_dict['compound_id'] = mol.compound_id
                        search_dict['img_file'] = mol.img_file
                        search_dict['smiles'] = mol.smiles
                        search_dict['MW'] = mol.MW
                        search_dict['TPSA'] = mol.TPSA
                        search_dict['mol_file_path'] = mol.mol_file_path
                        search_dict['similarity'] = 1
                        search_dict['xlogp'] = round(mol.xlogp, 3)
                        search_result.append(search_dict)
            if qf == '>':
                for mol in mol_list:
                    search_dict = {}
                    if mol.MW > mw_value:
                        search_dict['compound_id'] = mol.compound_id
                        search_dict['img_file'] = mol.img_file
                        search_dict['smiles'] = mol.smiles
                        search_dict['MW'] = mol.MW
                        search_dict['TPSA'] = mol.TPSA
                        search_dict['mol_file_path'] = mol.mol_file_path
                        search_dict['similarity'] = 'N/A'
                        search_dict['xlogp'] = round(mol.xlogp, 3)
                        search_result.append(search_dict)
            if qf == '=':
                for mol in mol_list:
                    search_dict = {}
                    if mol.MW == mw_value:
                        search_dict['compound_id'] = mol.compound_id
                        search_dict['img_file'] = mol.img_file
                        search_dict['smiles'] = mol.smiles
                        search_dict['MW'] = mol.MW
                        search_dict['TPSA'] = mol.TPSA
                        search_dict['mol_file_path'] = mol.mol_file_path
                        search_dict['similarity'] = 'N/A'
                        search_dict['xlogp'] = round(mol.xlogp, 3)
                        search_result.append(search_dict)
                #else:
                #   return HttpResponse('没有检索到包含此ID的化合物！')
            if len(search_result) == 0:
                html = '<center><p>没有检索到包此MW范围的化合物！</p></br><a href = \'/search/\'>返回搜索页面</a></center>'
                return HttpResponse(html)
            else:
                username = request.session['username']
                search_result_sorted = sorted(search_result, key=operator.itemgetter('MW'), reverse=False)
            return render(request, 'search_result.html', {'search_result_sorted': search_result_sorted,'username':username})
        else:
            return redirect('/search/')
    else:
        return redirect("/login/")


def upload(request):
    #upload_user = request.session['username']
    if request.method == 'GET':
        #return render(request,'upload.html')
        return HttpResponse("bad")
    elif request.method == 'POST':
        file_content = request.FILES.get("file-uploader", None)
        if not file_content:
            return HttpResponse("没有上传内容")
        else:
            if file_content.name.split('.')[1] != 'sdf':
                return HttpResponse("不是sdf文件，请上传sdf文件！")
            file_upload = os.path.join('./register/template/static/file_upload/', file_content.name)
            #获取上传文件的文件名，并将其存储到指定位置
            #print(file_upload)
            storage = open(file_upload,'wb+')       #打开存储文件
            for chunk in file_content.chunks():       #分块写入文件
                storage.write(chunk)
            storage.close()
            sdfs = [sdf for sdf in Chem.SDMolSupplier(file_upload)]
            for sdf in sdfs:
                smiles_from_sdfile = Chem.MolToSmiles(sdf)
                smiles = rdkit.Chem.CanonSmiles(smiles_from_sdfile, useChiral=1)
                #print(smiles)
                mol = Chem.MolFromSmiles(smiles)
                tpsa = round(Descriptors.TPSA(mol), 3)
                logp = round(Descriptors.MolLogP(mol), 3)
                mw = round(Descriptors.MolWt(mol), 3)
                if mol_props.objects.all().count() != 0:
                    compound_id_last = mol_props.objects.order_by('-compound_id').first().compound_id
                    #print(compound_id_last)
                    id = compound_id_last.split('-')[1]
                    id_1 = int(id)+1
                    id_2 = str(id_1).zfill(6)
                    compound_id = 'QL-' + id_2
                    # 分子图片输出
                    d = rdMolDraw2D.MolDraw2DCairo(300, 300)
                    d.DrawMolecule(mol)
                    d.FinishDrawing()
                    d.WriteDrawingText('./register/template/static/mol_image/%s.png' % compound_id)
                    img_path = '/static/mol_image/%s.png' % compound_id
                else:
                    compound_id = 'QL-000001'
                    # 分子图片输出
                    d = rdMolDraw2D.MolDraw2DCairo(300, 300)
                    d.DrawMolecule(mol)
                    d.FinishDrawing()
                    d.WriteDrawingText('./register/template/static/mol_image/%s.png' % compound_id)
                    img_path = '/static/mol_image/%s.png' % compound_id
                mol_file_tmp = open('./register/template/static/mol_file/%s.mol' % compound_id, 'w')
                mol_file_tmp.write(Chem.MolToMolBlock(mol))
                mol_file_tmp.close()
                mol_file_path = '/static/mol_file/%s.mol' % compound_id
                mol_write = Chem.MolToMolBlock(mol)
                fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2).ToBitString()
                if mol_props.objects.filter(smiles=smiles).exists():
                    html = '<center><p>化合物已存在，请勿重复注册！</p></br><a href = \'/index/\'>返回首页</a></center>'
                    return HttpResponse(html)
                else:
                    molecule_insert = mol_props.objects.create(compound_id=compound_id, smiles=smiles, mol_file=mol_write, TPSA=tpsa, xlogp=logp, MW=mw, img_file=img_path, fingerprint=fp, mol_file_path=mol_file_path)
                    molecule_insert.save()
            html = '<center><p>sdf批量上传成功！</p></br><a href = \'/compoundlist/\'>Compound List</a></center>'
            return HttpResponse(html)
    else:
        return HttpResponse("不支持的请求方法")
