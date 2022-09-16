import operator
import os
import time
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rdkit import Chem, DataStructs
import rdkit
from rdkit.Chem import AllChem, Descriptors
from rdkit.Chem.Draw import rdMolDraw2D
from .models import mol_props, cutome_fields_data, cutome_fields_dictionary,reagents,salts
import datetime
from . import models
from user.models import UsersInfo
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import pubchempy as pcp, requests, random
from django.forms.models import model_to_dict

def index(request):
    if request.session.get('is_login'):
        customed_value_list = cutome_fields_dictionary.objects.all()
        project = cutome_fields_dictionary.objects.filter(field_name='project').values_list('field_value', flat=True)
        from_supplier = cutome_fields_dictionary.objects.filter(field_name='from_supplier').values_list('field_value', flat=True)
        salt = cutome_fields_dictionary.objects.filter(field_name='salt').values_list('field_value',flat=True)
        stoich = cutome_fields_dictionary.objects.filter(field_name='stoich').values_list('field_value',flat=True)
        appearance =  cutome_fields_dictionary.objects.filter(field_name='appearance').values_list('field_value',flat=True)
        location = cutome_fields_dictionary.objects.filter(field_name='location').values_list('field_value',flat=True)
        weight_unit = cutome_fields_dictionary.objects.filter(field_name='weight_unit').values_list('field_value', flat=True)
        chiral = cutome_fields_dictionary.objects.filter(field_name='chiral').values_list('field_value',flat=True)
        now = datetime.datetime.now()
        registration_time = now.strftime("%Y-%m-%d %H:%M")
        username = request.session.get('username')
        user_info = UsersInfo.objects.get(username=username)
        #print(registration_time)
        return render(request,'index.html', locals())


    else:
        return redirect("/login/")


def registration(request):
    if request.method == 'POST':
        username = request.session.get('username')
        user_info = UsersInfo.objects.get(username=username)
        if request.POST.get('getsmiles') != '':
            #分子属性及ID
            smiles = request.POST.get('getsmiles')
            mol_check = Chem.MolFromSmiles(smiles)
            if mol_check is None:
                html = '<center><p>化合物结构错误，请重新输入！</p></br><a href = \'/index/\'>返回首页</a></center>'
                return HttpResponse(html)
            else:
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
                ctx = {}
                ctx['tpsa'] = tpsa
                ctx['logp'] = logp
                ctx['mw'] = mw
                ctx['compound_id'] = compound_id
                ctx['img_path'] = img_path
                ctx['smiles'] = smiles
                #处理自定义数据
                ctx['project'] = request.POST.get('project')
                ctx['registrar'] = request.POST.get('registrar')
                ctx['from_supplier'] = request.POST.get('from_supplier')
                ctx['weight'] = request.POST.get('weight')
                ctx['weight_unit'] = request.POST.get('weight_unit')
                ctx['supplier_ref'] = request.POST.get('supplier_ref')
                ctx['registration_time'] = request.POST.get('registration_time')
                ctx['appearance'] = request.POST.get('appearance')
                ctx['location'] = request.POST.get('location')
                ctx['chiral'] = request.POST.get('chiral')
                ctx['salt'] = request.POST.get('salt')
                ctx['stoich'] = request.POST.get('stoich')
                ctx['comments'] = request.POST.get('comments')
                ctx['username'] = username
                ctx['user_info'] = user_info
                return render(request, 'registration.html', ctx)
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
        #取到自定义字段
        project = request.POST.get('project')
        registrar = request.POST.get('registrar')
        from_supplier = request.POST.get('from_supplier')
        supplier_ref = request.POST.get('supplier_ref')
        registration_time = request.POST.get('registration_time')
        salt = request.POST.get('salt')
        stoich = request.POST.get('stoich')
        comments = request.POST.get('comments')
        appearance = request.POST.get('appearance')
        location = request.POST.get('location')
        chiral = request.POST.get('chiral')
        weight = request.POST.get('weight')
        weight_unit = request.POST.get('weight_unit')
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
            molecule_insert_1 = mol_props.objects.create(compound_id=compound_id, smiles=smiles, mol_file=mol, TPSA=tpsa, xlogp=logp, MW=mw, img_file=img_path, fingerprint=fp, mol_file_path=mol_file_path)
            molecule_insert_1.save()
            molecule_insert_2 = cutome_fields_data.objects.create(compound_id=compound_id,project=project,registrar=registrar,from_supplier=from_supplier,appearance=appearance,location=location,chiral=chiral,
                                                                 weight=weight,weight_unit=weight_unit,supplier_ref=supplier_ref,registration_time=registration_time,salt=salt,stoich=stoich,comments=comments)
            molecule_insert_2.save()
            html = '<center><p>化合物注册成功！</p></br><a href = \'/compoundlist/\'>Compound List</a></center>'
            return HttpResponse(html)


def delete_compound(request):
    if request.session.get('is_login'):
        delete_compound_id = request.GET.get('delete_compound_id')
        username = request.session['username']
        user_info = UsersInfo.objects.get(username=username)
        if mol_props.objects.filter(compound_id=delete_compound_id).exists():
            edit_compound_item = mol_props.objects.get(compound_id=delete_compound_id)
            image_path = edit_compound_item.img_file
        return render(request, "confirm_delete_compound.html", locals())
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
        username = request.session.get('username')
        user_info = UsersInfo.objects.get(username=username)
        if request.method == 'GET':
            edit_compound_id = request.GET.get('edit_compound_id')
            compound_data = cutome_fields_data.objects.get(compound_id=edit_compound_id)
            customed_value_list = cutome_fields_dictionary.objects.all()
            project = cutome_fields_dictionary.objects.filter(field_name='project').values_list('field_value',flat=True)
            from_supplier = cutome_fields_dictionary.objects.filter(field_name='from_supplier').values_list('field_value', flat=True)
            salt = cutome_fields_dictionary.objects.filter(field_name='salt').values_list('field_value', flat=True)
            stoich = cutome_fields_dictionary.objects.filter(field_name='stoich').values_list('field_value', flat=True)
            appearance = cutome_fields_dictionary.objects.filter(field_name='appearance').values_list('field_value',flat=True)
            location = cutome_fields_dictionary.objects.filter(field_name='location').values_list('field_value',flat=True)
            weight_unit = cutome_fields_dictionary.objects.filter(field_name='weight_unit').values_list('field_value',flat=True)
            chiral = cutome_fields_dictionary.objects.filter(field_name='chiral').values_list('field_value', flat=True)
            return render(request, "edit_compound.html", locals())
        if request.method == 'POST':
            edit_compound_id = request.POST.get('edit_compound_id')
            update_item = mol_props.objects.get(compound_id=edit_compound_id)
            update_edit_smiles = request.POST.get('update_edit_smiles')
            if Chem.MolFromSmiles(update_edit_smiles) is None:
                html = '<center><p>结构有误，请重新输入！</p></br><a href = \'http://localhost:8000/edit_compound/?edit_compound_id=%s\'>返回</a></center>' % edit_compound_id
                return HttpResponse(html)
            elif update_edit_smiles == update_item.smiles:
                mol_custom_data = cutome_fields_data.objects.get(compound_id=edit_compound_id)
                new_project = request.POST.get('project')
                new_supplier = request.POST.get('from_supplier')
                new_weight = request.POST.get('weight')
                new_weight_unit = request.POST.get('weight_unit')
                new_supplier_ref = request.POST.get('supplier_ref')
                new_location = request.POST.get('location')
                new_appearance = request.POST.get('appearance')
                new_stoich = request.POST.get('stoich')
                new_chiral = request.POST.get('chiral')
                new_salt = request.POST.get('salt')
                new_comments = request.POST.get('comments')
                if mol_custom_data.project == new_project and\
                    mol_custom_data.from_supplier == new_supplier and\
                    str(mol_custom_data.weight) == new_weight and\
                    mol_custom_data.weight_unit == new_weight_unit and\
                    mol_custom_data.supplier_ref == new_supplier_ref and\
                    mol_custom_data.location == new_location and\
                    mol_custom_data.appearance == new_appearance and\
                    mol_custom_data.stoich == new_stoich and\
                    mol_custom_data.chiral == new_chiral and\
                    mol_custom_data.salt == new_salt and\
                    mol_custom_data.comments == new_comments:
                    html = '<center><p>未做任何修改！</p></br><a href = \'http://localhost:8000/edit_compound/?edit_compound_id=%s\'>返回</a></center>' % edit_compound_id
                    return HttpResponse(html)
                else:
                    update_custom_item = cutome_fields_data.objects.get(compound_id=edit_compound_id)
                    update_custom_item.project = new_project
                    update_custom_item.from_supplier = new_supplier
                    update_custom_item.weight = new_weight
                    update_custom_item.weight_unit = new_weight_unit
                    update_custom_item.supplier_ref = new_supplier_ref
                    update_custom_item.location = new_location
                    update_custom_item.appearance = new_appearance
                    update_custom_item.stoich = new_stoich
                    update_custom_item.chiral = new_chiral
                    update_custom_item.salt = new_salt
                    update_custom_item.comments = new_comments
                    update_custom_item.save()
                    html = '<center><p>更新成功</p></br><a href = \'http://localhost:8000/edit_compound/?edit_compound_id=%s\'>返回</a></center>' % edit_compound_id
                    return HttpResponse(html)
            else:
                mol_file_path = './register/template/static/mol_file/%s.mol' % edit_compound_id
                mol_img_path = './register/template/static/mol_image/%s.png' % edit_compound_id
                if os.path.exists(mol_file_path):
                    os.remove(mol_file_path)
                if os.path.exists(mol_img_path):
                    os.remove(mol_img_path)
                smiles = update_edit_smiles
                mol_mem = Chem.MolFromSmiles(smiles)
                tpsa = round(Descriptors.TPSA(mol_mem), 3)
                logp = round(Descriptors.MolLogP(mol_mem), 3)
                mw = round(Descriptors.MolWt(mol_mem), 3)
                mol = Chem.MolToMolBlock(mol_mem)
                mol_file_tmp = open('./register/template/static/mol_file/%s.mol' % edit_compound_id, 'w')
                mol_file_tmp.write(mol)
                mol_file_tmp.close()
                mol_file_path = '/static/mol_file/%s.mol' % edit_compound_id
                d = rdMolDraw2D.MolDraw2DCairo(300, 300)
                d.DrawMolecule(mol_mem)
                d.FinishDrawing()
                d.WriteDrawingText('./register/template/static/mol_image/%s.png' % edit_compound_id)
                img_path = '/static/mol_image/%s.png' % edit_compound_id
                fp = AllChem.GetMorganFingerprintAsBitVect(mol_mem, radius=2).ToBitString()
                # print(fp)
                if mol_props.objects.filter(smiles=smiles).exists():
                    html = '<center><p>化合物已存在！</p></br><a href = \'http://localhost:8000/edit_compound/?edit_compound_id=%s\'>返回</a></center>' % edit_compound_id
                    return HttpResponse(html)
                else:
                    update_item.compound_id = edit_compound_id
                    update_item.smiles = smiles
                    update_item.mol_file = mol
                    update_item.TPSA = tpsa
                    update_item.xlogp = logp
                    update_item.MW = mw
                    update_item.img_file = img_path
                    update_item.fingerprint = fp
                    update_item.mol_file_path = mol_file_path
                    update_item.save()
                new_project = request.POST.get('project')
                new_supplier = request.POST.get('from_supplier')
                new_weight = request.POST.get('weight')
                new_weight_unit = request.POST.get('weight_unit')
                new_supplier_ref = request.POST.get('supplier_ref')
                new_location = request.POST.get('location')
                new_appearance = request.POST.get('appearance')
                new_stoich = request.POST.get('stoich')
                new_chiral = request.POST.get('chiral')
                new_salt = request.POST.get('salt')
                new_comments = request.POST.get('comments')
                update_custom_item = cutome_fields_data.objects.get(compound_id=edit_compound_id)
                update_custom_item.project = new_project
                update_custom_item.from_supplier = new_supplier
                update_custom_item.weight = new_weight
                update_custom_item.weight_unit = new_weight_unit
                update_custom_item.supplier_ref = new_supplier_ref
                update_custom_item.location = new_location
                update_custom_item.appearance = new_appearance
                update_custom_item.stoich = new_stoich
                update_custom_item.chiral = new_chiral
                update_custom_item.salt = new_salt
                update_custom_item.comments = new_comments
                update_custom_item.save()
                html = '<center><p>更新成功！</p></br><a href = \'http://localhost:8000/edit_compound/?edit_compound_id=%s\'>返回</a></center>' % edit_compound_id
                return HttpResponse(html)
    else:
        return redirect("/login/")


def compoundlist(request):
    if request.session.get('is_login'):
        username = request.session.get('username')
        user_info = UsersInfo.objects.get(username=username)
        if request.method == 'POST':
            query_smiles_s = request.POST.get('query_smiles')
            compound_id_s = request.POST.get('compound_id')
            project_s = request.POST.get('project')
            registrar_s = request.POST.get('registrar')
            supplier_s = request.POST.get('from_supplier')
            weights_s = request.POST.get('weights')
            weightl_s = request.POST.get('weightl')
            weight_unit_s = request.POST.get('weight_unit')
            supplier_ref_s = request.POST.get('supplier_ref')
            registration_times = request.POST.get('registration_times')
            registration_timel = request.POST.get('registration_timel')
            salt_s = request.POST.get('salt')
            appearance_s = request.POST.get('appearance')
            stoich_s = request.POST.get('stoich')
            location_s = request.POST.get('location')
            chiral_s = request.POST.get('chiral')
            comments_s = request.POST.get('comments')
            mws_s = request.POST.get('mws')
            mwl_s = request.POST.get('mwl')
            tpsas_s = request.POST.get('tpsas')
            tpsal_s = request.POST.get('tpsal')
            logps_s = request.POST.get('logps')
            logpl_s = request.POST.get('logpl')

            # substructure search
            query_smiles = request.POST.get('query_smiles')
            mol_list = []
            if query_smiles != '':
                mols= mol_props.objects.all()
                for mol in mols:
                    m = Chem.MolFromSmiles(mol.smiles)
                    if m.HasSubstructMatch(Chem.MolFromSmiles(query_smiles)):
                        mol_list.append(mol.smiles)
            if query_smiles == '':
                mols = mol_props.objects.all()
                for mol in mols:
                    mol_list.append(mol.smiles)
            # substructure search

            # build query set
            query_set_ori = cutome_fields_data.objects \
            .filter(compound__compound_id__icontains=compound_id_s) \
            .filter(compound__smiles__in=mol_list)\
            .filter(project__icontains=project_s) \
            .filter(registrar__icontains=registrar_s) \
            .filter(from_supplier__icontains=supplier_s) \
            .filter(weight__gte=weights_s).filter(weight__lte=weightl_s) \
            .filter(weight_unit__icontains=weight_unit_s)\
            .filter(supplier_ref__icontains=supplier_ref_s) \
            .filter(registration_time__gte=registration_times).filter(registration_time__lte=registration_timel)\
            .filter(salt__icontains=salt_s)\
            .filter(appearance__icontains=appearance_s) \
            .filter(stoich__icontains=stoich_s) \
            .filter(location__icontains=location_s) \
            .filter(chiral__icontains=chiral_s) \
            .filter(comments__icontains=comments_s) \
            .filter(compound__MW__gte=mws_s).filter(compound__MW__lte=mwl_s) \
            .filter(compound__TPSA__gte=tpsas_s).filter(compound__TPSA__lte=tpsal_s) \
            .filter(compound__xlogp__gte=logps_s).filter(compound__xlogp__lte=logpl_s) \

            query_set = query_set_ori.order_by('-compound_id')
            # build query set

            #render drop down lsit
            customed_value_list = cutome_fields_dictionary.objects.all()
            project = cutome_fields_dictionary.objects.filter(field_name='project').values_list('field_value',flat=True)
            from_supplier = cutome_fields_dictionary.objects.filter(field_name='from_supplier').values_list('field_value', flat=True)
            salt = cutome_fields_dictionary.objects.filter(field_name='salt').values_list('field_value', flat=True)
            stoich = cutome_fields_dictionary.objects.filter(field_name='stoich').values_list('field_value', flat=True)
            appearance = cutome_fields_dictionary.objects.filter(field_name='appearance').values_list('field_value',flat=True)
            location = cutome_fields_dictionary.objects.filter(field_name='location').values_list('field_value',flat=True)
            weight_unit = cutome_fields_dictionary.objects.filter(field_name='weight_unit').values_list('field_value',flat=True)
            chiral = cutome_fields_dictionary.objects.filter(field_name='chiral').values_list('field_value', flat=True)
            # build query set

            # render drop down lsit
            # page paginator
            paginator = Paginator(query_set, 10)
            page = request.GET.get('page', 1)
            try:
                sublist = paginator.page(page)
            except PageNotAnInteger:
                sublist = paginator.page(1)
            except EmptyPage:
                sublist = paginator.page(paginator.num_pages)
            return render(request, "compoundlist.html", locals())
            # page paginator

        # when first enter compoundlist, transfer data
        customed_value_list = cutome_fields_dictionary.objects.all()
        project = cutome_fields_dictionary.objects.filter(field_name='project').values_list('field_value', flat=True)
        from_supplier = cutome_fields_dictionary.objects.filter(field_name='from_supplier').values_list('field_value',flat=True)
        salt = cutome_fields_dictionary.objects.filter(field_name='salt').values_list('field_value', flat=True)
        stoich = cutome_fields_dictionary.objects.filter(field_name='stoich').values_list('field_value', flat=True)
        appearance = cutome_fields_dictionary.objects.filter(field_name='appearance').values_list('field_value',flat=True)
        location = cutome_fields_dictionary.objects.filter(field_name='location').values_list('field_value', flat=True)
        weight_unit = cutome_fields_dictionary.objects.filter(field_name='weight_unit').values_list('field_value',flat=True)
        chiral = cutome_fields_dictionary.objects.filter(field_name='chiral').values_list('field_value', flat=True)

        custome_field_list = cutome_fields_data.objects.all().order_by('-compound_id')
        paginator = Paginator(custome_field_list, 10)
        page = request.GET.get('page', 1)
        try:
            sublist = paginator.page(page)
        except PageNotAnInteger:
            sublist = paginator.page(1)
        except EmptyPage:
            sublist = paginator.page(paginator.num_pages)
        return render(request, "compoundlist.html", locals())
        # when first enter compoundlist
    else:
        return redirect("/login/")


def upload(request):
    #upload_user = request.session['username']
    if request.method == 'GET':
        #return render(request,'upload.html')
        return HttpResponse("None")
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


def custome_fields(request):
    if request.session.get('is_login'):
        username = request.session['username']
        user_info = UsersInfo.objects.get(username=username)
        if request.method == 'GET':
            if request.GET.get('query_field'):
                query_field = request.GET.get('query_field')
                customed_field_value = cutome_fields_dictionary.objects.filter(field_name=query_field).values_list(
                    'field_value', flat=True)
                fieldlist = []
                for field in cutome_fields_data._meta.fields:
                    field_need_custome = str(field).split('.')[-1]
                    if not ['id', 'compound_id', 'batch_id', 'registrar', 'supplier_ref', 'registration_time',
                            'comments', 'weight'].__contains__(field_need_custome):
                        fieldlist.append(field_need_custome)
                return render(request, 'custome_fields.html', locals())
            if request.GET.get('delete_field') and request.GET.get('delete_value'):
                delete_field = request.GET.get('delete_field')
                delete_value_ori = request.GET.get('delete_value')
                delete_value = delete_value_ori.replace('-','#')
                #delete_value = delete_value.replace('%20',' ')
                print(delete_value)
                for i in delete_value.rstrip(',').split(','):
                    custome_field = cutome_fields_dictionary.objects.filter(field_name=delete_field)
                    for j in custome_field:
                        if i == j.field_value:
                            custome_field.filter(field_value=i).delete()
                message = '删除成功！'
                username = request.session['username']
                fieldlist = []
                for field in cutome_fields_data._meta.fields:
                    field_need_custome = str(field).split('.')[-1]
                    if not ['id', 'compound_id','compound', 'batch_id', 'registrar', 'supplier_ref', 'registration_time',
                            'comments', 'weight'].__contains__(field_need_custome):
                        fieldlist.append(field_need_custome)
                return render(request, 'custome_fields.html', locals())

        if request.method == 'POST':
            if request.POST.get('custome_field') and request.POST.get('custome_value'):
                custome_field = request.POST.get('custome_field')
                query_field = custome_field
                custome_value = request.POST.get('custome_value')
                customed_field_value = cutome_fields_dictionary.objects.filter(field_name=custome_field).values_list(
                    'field_value', flat=True)
                #print(custome_field, custome_value)
                if cutome_fields_dictionary.objects.filter(field_name=custome_field).exists():
                    customed_value_list= cutome_fields_dictionary.objects.filter(field_name=custome_field).values_list('field_value',flat=True)
                    if custome_value == '':
                        message = '失败！添加了空值'
                        username = request.session['username']
                        fieldlist = []
                        for field in cutome_fields_data._meta.fields:
                            field_need_custome = str(field).split('.')[-1]
                            if not ['id', 'compound_id', 'batch_id', 'registrar', 'supplier_ref', 'registration_time',
                                    'comments', 'weight'].__contains__(field_need_custome):
                                fieldlist.append(field_need_custome)
                        return render(request, locals())
                    if custome_value in customed_value_list:
                        return HttpResponse("已存在！")
                    else:
                        field_insert = cutome_fields_dictionary.objects.create(field_name=custome_field, field_value=custome_value)
                        field_insert.save()
                        message = '添加成功'
                        username = request.session['username']
                        fieldlist = []
                        for field in cutome_fields_data._meta.fields:
                            field_need_custome = str(field).split('.')[-1]
                            if not ['id', 'compound_id', 'batch_id', 'registrar', 'supplier_ref', 'registration_time',
                                    'comments', 'weight'].__contains__(field_need_custome):
                                fieldlist.append(field_need_custome)
                        return render(request,'custome_fields.html',locals())
                if not cutome_fields_dictionary.objects.filter(field_name=custome_field).exists():
                    field_insert = cutome_fields_dictionary.objects.create(field_name=custome_field, field_value=custome_value)
                    field_insert.save()
                    message = '添加成功'
                    username = request.session['username']
                    fieldlist = []
                    for field in cutome_fields_data._meta.fields:
                        field_need_custome = str(field).split('.')[-1]
                        if not ['id', 'compound_id', 'batch_id', 'registrar', 'supplier_ref', 'registration_time',
                                'comments', 'weight'].__contains__(field_need_custome):
                            fieldlist.append(field_need_custome)
                    return render(request, 'custome_fields.html', locals())
            else:
                message = '失败，没有获取到数值！'
                username = request.session['username']
                fieldlist = []
                for field in cutome_fields_data._meta.fields:
                    field_need_custome = str(field).split('.')[-1]
                    if not ['id', 'compound_id', 'batch_id', 'registrar', 'supplier_ref', 'registration_time',
                            'comments', 'weight'].__contains__(field_need_custome):
                        fieldlist.append(field_need_custome)
                return render(request, 'custome_fields.html',
                              locals())
        else:
            username = request.session['username']
            fieldlist = []
            for field in cutome_fields_data._meta.fields:
                field_need_custome = str(field).split('.')[-1]
                if not ['id', 'compound_id', 'batch_id', 'registrar','supplier_ref','registration_time','comments','weight'].__contains__(field_need_custome):
                    fieldlist.append(field_need_custome)
            #print(fieldlist)
            return render(request, 'custome_fields.html', locals())

    else:
        return redirect('login/')


def reagentlist(request):
    if request.session.get('is_login'):
        username = request.session.get('username')
        user_info = UsersInfo.objects.get(username=username)
        if request.method == 'POST':
            reagent_smiles = request.POST.get('reagentsmiles')
            if reagents.objects.filter(smiles=reagent_smiles).exists():
                message = 'Reagent existed!'
                reagent_list = reagents.objects.all().order_by('-reagentid')
                return render(request, 'reagentlist.html', locals())
            else:
                cid_for_reagent = pcp.get_compounds(reagent_smiles, "smiles")[0].cid
                url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/%s/JSON/?heading=CAS" % cid_for_reagent
                user_agent = [
                    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
                    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
                    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
                    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
                    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
                    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
                    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
                    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
                    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
                    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
                    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
                    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
                    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
                    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
                    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
                ]
                response = requests.get(url, headers={'User-Agent': random.choice(user_agent), "connection": "close"},
                                        timeout=5,
                                        verify=False)
                reagent_casnum = response.json()['Record']['Section'][0]['Section'][0]['Section'][0]["Information"][0]['Value'][
                    'StringWithMarkup'][0]['String']
                reagent = pcp.Compound.from_cid(cid_for_reagent)
                reagent_iupac = reagent.iupac_name
                registration_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                #print(reagent_casnum,reagent_iupac)
                if reagents.objects.filter(name=reagent_iupac).exists():
                    message = 'Reagent existed!'
                    reagent_list = reagents.objects.all().order_by('-reagentid')
                    return render(request, 'reagentlist.html', locals())
                else:
                    reagent_mol = Chem.MolFromSmiles(reagent_smiles)
                    mw = round(Descriptors.MolWt(reagent_mol), 3)
                    if reagents.objects.all().count() != 0:
                        reagent_id_last = reagents.objects.order_by('-reagentid').first().reagentid
                        # print(compound_id_last)
                        id = reagent_id_last.split('-')[1]
                        id_1 = int(id) + 1
                        id_2 = str(id_1).zfill(6)
                        reagent_id = 'Reagent-' + id_2
                        # 分子图片输出
                        d = rdMolDraw2D.MolDraw2DCairo(300, 300)
                        d.DrawMolecule(reagent_mol)
                        d.FinishDrawing()
                        d.WriteDrawingText('./register/template/static/reagent_image/%s.png' % reagent_id)
                        img_path = '/static/reagent_image/%s.png' % reagent_id
                    else:
                        reagent_id = 'Reagent-000001'
                        # 分子图片输出
                        d = rdMolDraw2D.MolDraw2DCairo(300, 300)
                        d.DrawMolecule(reagent_mol)
                        d.FinishDrawing()
                        d.WriteDrawingText('./register/template/static/reagent_image/%s.png' % reagent_id)
                        img_path = '/static/reagent_image/%s.png' % reagent_id
                    reagents_insert = reagents.objects.create(registration_time=registration_time,MW=mw,reagentid=reagent_id,smiles = reagent_smiles,name = reagent_iupac,reagent_img_path = img_path,cas_no=reagent_casnum)
                    reagents_insert.save()
                    message = 'Success!'
                    reagent_list = reagents.objects.all().order_by('-reagentid')
                    return render(request,'reagentlist.html',locals())
        if request.method == 'GET':
            sub_reagent_smiles_s = request.GET.get('sub_reagent_smiles')
            reagent_list = []
            if not sub_reagent_smiles_s:
                sub_reagent_smiles_s = ''
                reagents_all = reagents.objects.all()
                for reagent in reagents_all:
                    reagent_list.append(reagent.smiles)
            else:
                reagents_all = reagents.objects.all()
                for reagent in reagents_all:
                    m = Chem.MolFromSmiles(reagent.smiles)
                    if m.HasSubstructMatch(Chem.MolFromSmiles(sub_reagent_smiles_s)):
                        reagent_list.append(reagent.smiles)

            sub_reagent_id_s = request.GET.get('sub_reagent_id')
            if not sub_reagent_id_s:
                sub_reagent_id_s = ''
            sub_reagent_iupac_name_s= request.GET.get('sub_reagent_iupac_name')
            if not sub_reagent_iupac_name_s:
                sub_reagent_iupac_name_s = ''
            sub_reagent_cas_no_s = request.GET.get('sub_reagent_cas_no')
            if not sub_reagent_cas_no_s:
                sub_reagent_cas_no_s = ''
            sub_mws_s = request.GET.get('mws')
            if not sub_mws_s:
                sub_mws_s = '-Infinity'
            sub_mwl_s = request.GET.get('mwl')
            if not sub_mwl_s:
                sub_mwl_s = 'Infinity'
            registration_times_s = request.GET.get('registration_times_s')
            if not registration_times_s:
                registration_times_s = '1900-01-01 10:00'
            registration_timel_s = request.GET.get('registration_timel_s')
            if not registration_timel_s:
                registration_timel_s = '2100-01-01 10:00'

            reagent_query_set_ori = reagents.objects \
                .filter(smiles__in = reagent_list)\
                .filter(reagentid__icontains=sub_reagent_id_s) \
                .filter(name__icontains=sub_reagent_iupac_name_s) \
                .filter(cas_no__icontains=sub_reagent_cas_no_s)\
                .filter(MW__gte=sub_mws_s).filter(MW__lte=sub_mwl_s) \
                .filter(registration_time__gte=registration_times_s).filter(registration_time__lte=registration_timel_s)
            reagent_list = reagent_query_set_ori.order_by('-reagentid')
            return render(request, 'reagentlist.html', locals())
    else:
        return redirect('/login/')


def saltlist(request):
    if request.session.get('is_login'):
        username = request.session.get('username')
        user_info = UsersInfo.objects.get(username=username)
        if request.method == 'POST':
            salt_smiles = request.POST.get('saltsmiles')
            if salts.objects.filter(smiles=salt_smiles).exists():
                message = 'Salt existed!'
                salt_list = salts.objects.all().order_by('-saltid')
                return render(request, 'saltlist.html', locals())
            else:
                cid_for_salt = pcp.get_compounds(salt_smiles, "smiles")[0].cid
                url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/%s/JSON/?heading=CAS" % cid_for_salt
                user_agent = [
                    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
                    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
                    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
                    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
                    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
                    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
                    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
                    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
                    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
                    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
                    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
                    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
                    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
                    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
                    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
                ]
                response = requests.get(url, headers={'User-Agent': random.choice(user_agent), "connection": "close"},
                                        timeout=5,
                                        verify=False)
                salt_casnum = response.json()['Record']['Section'][0]['Section'][0]['Section'][0]["Information"][0]['Value'][
                    'StringWithMarkup'][0]['String']
                salt = pcp.Compound.from_cid(cid_for_salt)
                salt_iupac = salt.iupac_name
                registration_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                #print(reagent_casnum,reagent_iupac)
                if salts.objects.filter(name=salt_iupac).exists():
                    message = 'Salt existed!'
                    salt_list = reagents.objects.all().order_by('-saltid')
                    return render(request, 'saltlist.html', locals())
                else:
                    salt_mol = Chem.MolFromSmiles(salt_smiles)
                    mw = round(Descriptors.MolWt(salt_mol), 3)
                    if salts.objects.all().count() != 0:
                        salt_id_last = salts.objects.order_by('-saltid').first().saltid
                        # print(compound_id_last)
                        id = salt_id_last.split('-')[1]
                        id_1 = int(id) + 1
                        id_2 = str(id_1).zfill(6)
                        salt_id = 'Salt-' + id_2
                        # 分子图片输出
                        d = rdMolDraw2D.MolDraw2DCairo(300, 300)
                        d.DrawMolecule(salt_mol)
                        d.FinishDrawing()
                        d.WriteDrawingText('./register/template/static/salt_image/%s.png' % salt_id)
                        img_path = '/static/salt_image/%s.png' % salt_id
                    else:
                        salt_id = 'Salt-000001'
                        # 分子图片输出
                        d = rdMolDraw2D.MolDraw2DCairo(300, 300)
                        d.DrawMolecule(salt_mol)
                        d.FinishDrawing()
                        d.WriteDrawingText('./register/template/static/salt_image/%s.png' % salt_id)
                        img_path = '/static/salt_image/%s.png' % salt_id
                    salts_insert = salts.objects.create(registration_time=registration_time,MW=mw,saltid=salt_id,name = salt_iupac,salt_img_path = img_path,cas_no=salt_casnum)
                    salts_insert.save()
                    message = 'Success!'
                    salt_list = salts.objects.all().order_by('-saltid')
                    return render(request,'saltlist.html',locals())
        salt_list = salts.objects.all().order_by('-saltid')
        return render(request, 'saltlist.html', locals())
    else:
        return redirect('/login/')

def details(request):
    if request.session.get('is_login'):
        username = request.session.get('username')
        user_info = UsersInfo.objects.get(username=username)
        compound_id = request.GET.get('compound_id')
        item = cutome_fields_data.objects.get(compound_id=compound_id)
        item_dict = model_to_dict(item,exclude=['id','compound','batch_id'])
        item_primary = item.compound
        item_primary_dict = model_to_dict(item_primary,exclude=['mol_file', 'mol_file_path', 'smiles', 'img_file', 'fingerprint'])

        smiles = item.compound.smiles
        cid = pcp.get_compounds(smiles, "smiles")[0].cid
        if cid:
            compound = pcp.Compound.from_cid(cid)
            compound_iupac = compound.iupac_name
            url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/%s/JSON/?heading=CAS" % cid
            user_agent = [
                "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
                "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
                "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
                "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
                "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
                "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
                "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
                "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
                "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
                "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
                "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
                "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
                "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
                "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
            ]
            response = requests.get(url, headers={'User-Agent': random.choice(user_agent), "connection": "close"},
                                    timeout=5,
                                    verify=False)
            if response:
                casnum = response.json()['Record']['Section'][0]['Section'][0]['Section'][0]["Information"][0]['Value']['StringWithMarkup'][0]['String']
            else:
                casnum='None'
        else:
            compound_iupac='No retrieved name'
            casnum = 'None'
        return render(request, 'details.html', locals())
    else:
        return redirect('/login/')


# def search(request):
#     if request.session.get('is_login'):
#         username = request.session.get('username')
#         user_info = UsersInfo.objects.get(username=username)
#         return render(request, "search.html",locals())
#     else:
#         return redirect('/login/')
#
#
# def search_result(request):
#     if request.session.get('is_login'):
#         username = request.session.get('username')
#         user_info = UsersInfo.objects.get(username=username)
#         ##相似性结构检索，输入Similarity数值以及不输入Similarity数值
#         if request.POST.get('getsearchsmiles') != '' and request.POST.get('similarity') != '':
#             getsearchsmiles = rdkit.Chem.CanonSmiles(request.POST.get('getsearchsmiles'), useChiral=1)
#             getsimilarity = float(request.POST.get('similarity'))
#             getsearchmol = Chem.MolFromSmiles(getsearchsmiles)
#             getsearchmol_fp = Chem.AllChem.GetMorganFingerprint(getsearchmol, 2)
#             if getsearchmol:
#                 mol_list = mol_props.objects.all()
#                 search_result = []
#                 for item in mol_list:
#                     search_dict = {}
#                     smiles = item.smiles
#                     mol = Chem.MolFromSmiles(smiles)
#                     fp = Chem.AllChem.GetMorganFingerprint(mol, 2)
#                     similarity = DataStructs.DiceSimilarity(fp, getsearchmol_fp)
#                     if similarity > getsimilarity:
#                         search_dict['compound_id'] = item.compound_id
#                         search_dict['img_file'] = item.img_file
#                         search_dict['smiles'] = item.smiles
#                         search_dict['mol_file_path'] = item.mol_file_path
#                         search_dict['MW'] = item.MW
#                         search_dict['TPSA'] = item.TPSA
#                         search_dict['similarity'] = round(similarity, 3)
#                         search_dict['xlogp'] = round(item.xlogp, 3)
#                         search_result.append(search_dict)
#                 search_result_sorted = sorted(search_result, key=operator.itemgetter('similarity'), reverse=True)
#                 username = request.session['username']
#                 return render(request, 'search_result.html', locals())
#         if request.POST.get('getsearchsmiles') != '' and request.POST.get('similarity') == '':
#             html = '<center><p>请输入相似性数值！</p></br><a href = \'/search/\'>返回搜索页面</a></center>'
#             return HttpResponse(html)
#
#         ##属性检索Compound ID
#         if request.POST.get('compound_id') != '' and request.POST.get('similarity'):
#             compound_id = request.POST.get('compound_id')
#             mol_list = mol_props.objects.all()
#             search_result = []
#             for mol in mol_list:
#                 search_dict = {}
#                 if compound_id.upper() in mol.compound_id.upper():
#                     search_dict['compound_id'] = mol.compound_id
#                     search_dict['img_file'] = mol.img_file
#                     search_dict['smiles'] = mol.smiles
#                     search_dict['MW'] = mol.MW
#                     search_dict['mol_file_path'] = mol.mol_file_path
#                     search_dict['similarity'] = 'N/A'
#                     search_dict['TPSA'] = mol.TPSA
#                     search_dict['xlogp'] = round(mol.xlogp, 3)
#                     search_result.append(search_dict)
#                 #else:
#                  #   return HttpResponse('没有检索到包含此ID的化合物！')
#             if len(search_result) == 0:
#                 html = '<center><p>没有检索到包含此ID的化合物！</p></br><a href = \'/search/\'>返回搜索页面</a></center>'
#                 return HttpResponse(html)
#             else:
#                 username = request.session['username']
#                 search_result_sorted = sorted(search_result, key=operator.itemgetter('compound_id'), reverse=False)
#             return render(request, 'search_result.html', locals())
#
#         ##属性检索MW
#         if request.POST.get('mw_value') and request.POST.get('mw_qualifier') and request.POST.get('similarity') :
#             mw_value = float(request.POST.get('mw_value'))
#             qf = request.POST.get('mw_qualifier')
#             print(qf,mw_value)
#             mol_list = mol_props.objects.all()
#             search_result = []
#             if qf == '<':
#                 for mol in mol_list:
#                     search_dict = {}
#                     if mol.MW < mw_value:
#                         search_dict['compound_id'] = mol.compound_id
#                         search_dict['img_file'] = mol.img_file
#                         search_dict['smiles'] = mol.smiles
#                         search_dict['MW'] = mol.MW
#                         search_dict['TPSA'] = mol.TPSA
#                         search_dict['mol_file_path'] = mol.mol_file_path
#                         search_dict['similarity'] = 1
#                         search_dict['xlogp'] = round(mol.xlogp, 3)
#                         search_result.append(search_dict)
#             if qf == '>':
#                 for mol in mol_list:
#                     search_dict = {}
#                     if mol.MW > mw_value:
#                         search_dict['compound_id'] = mol.compound_id
#                         search_dict['img_file'] = mol.img_file
#                         search_dict['smiles'] = mol.smiles
#                         search_dict['MW'] = mol.MW
#                         search_dict['TPSA'] = mol.TPSA
#                         search_dict['mol_file_path'] = mol.mol_file_path
#                         search_dict['similarity'] = 'N/A'
#                         search_dict['xlogp'] = round(mol.xlogp, 3)
#                         search_result.append(search_dict)
#             if qf == '=':
#                 for mol in mol_list:
#                     search_dict = {}
#                     if mol.MW == mw_value:
#                         search_dict['compound_id'] = mol.compound_id
#                         search_dict['img_file'] = mol.img_file
#                         search_dict['smiles'] = mol.smiles
#                         search_dict['MW'] = mol.MW
#                         search_dict['TPSA'] = mol.TPSA
#                         search_dict['mol_file_path'] = mol.mol_file_path
#                         search_dict['similarity'] = 'N/A'
#                         search_dict['xlogp'] = round(mol.xlogp, 3)
#                         search_result.append(search_dict)
#                 #else:
#                 #   return HttpResponse('没有检索到包含此ID的化合物！')
#             if len(search_result) == 0:
#                 html = '<center><p>没有检索到包此MW范围的化合物！</p></br><a href = \'/search/\'>返回搜索页面</a></center>'
#                 return HttpResponse(html)
#             else:
#                 search_result_sorted = sorted(search_result, key=operator.itemgetter('MW'), reverse=False)
#             return render(request, 'search_result.html', locals())
#         else:
#             return redirect('/search/')
#     else:
#         return redirect("/login/")
