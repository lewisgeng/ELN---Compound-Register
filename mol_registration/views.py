import operator
import os
import time
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rdkit import Chem, DataStructs
import rdkit
from rdkit.Chem import AllChem, Descriptors
from rdkit.Chem.Draw import rdMolDraw2D
from .models import mol_props, cutome_fields_data, cutome_fields_dictionary
import datetime
from . import models
from user.models import UsersInfo
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


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
            smiles_original = request.POST.get('getsmiles')
            mol_check = Chem.MolFromSmiles(smiles_original)
            if mol_check is None:
                html = '<center><p>化合物结构错误，请重新输入！</p></br><a href = \'/index/\'>返回首页</a></center>'
                return HttpResponse(html)
            else:
                # convert to canonsmiles
                smiles = rdkit.Chem.CanonSmiles(smiles_original)
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
        smiles_original = request.POST.get('smiles')
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
            edit_compound_item = mol_props.objects.get(compound_id=edit_compound_id)
            ctx = {}
            origin_smiles= edit_compound_item.smiles
            edit_compound_id = edit_compound_id
            username = username
            return render(request, "edit_compound.html", locals())
        if request.method == 'POST':
            #update_edit_smiles = request.POST.get('update_edit_smiles')
            edit_compound_id = request.POST.get('edit_compound_id')
            print(edit_compound_id)
            if models.mol_props.objects.filter(compound_id=edit_compound_id).exists():
                update_item = mol_props.objects.get(compound_id=edit_compound_id)
                update_edit_smiles = request.POST.get('update_edit_smiles')
                print(update_edit_smiles)
                if Chem.MolFromSmiles(update_edit_smiles) is None:
                    html = '<center><p>结构有误，请重新输入！</p></br><a href = \'http://localhost:8000/edit_compound/?edit_compound_id=%s\'>返回</a></center>' % edit_compound_id
                    return HttpResponse(html)
                else:
                    if Chem.CanonSmiles(update_edit_smiles) == Chem.CanonSmiles(update_item.smiles):
                        html = '<center><p>结构未做任何修改！</p></br><a href = \'http://localhost:8000/edit_compound/?edit_compound_id=%s\'>返回</a></center>' % edit_compound_id
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
                        time.sleep(0.25)
                        # print(mol)
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
                            return HttpResponse('更新成功！')
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



def search(request):
    if request.session.get('is_login'):
        username = request.session.get('username')
        user_info = UsersInfo.objects.get(username=username)
        return render(request, "search.html",locals())
    else:
        return redirect('/login/')


def search_result(request):
    if request.session.get('is_login'):
        username = request.session.get('username')
        user_info = UsersInfo.objects.get(username=username)
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
                return render(request, 'search_result.html', locals())
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
            return render(request, 'search_result.html', locals())

        ##属性检索MW
        if request.POST.get('mw_value') and request.POST.get('mw_qualifier') and request.POST.get('similarity') :
            mw_value = float(request.POST.get('mw_value'))
            qf = request.POST.get('mw_qualifier')
            print(qf,mw_value)
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
                search_result_sorted = sorted(search_result, key=operator.itemgetter('MW'), reverse=False)
            return render(request, 'search_result.html', locals())
        else:
            return redirect('/search/')
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
                custome_value = request.POST.get('custome_value')
                print(custome_field, custome_value)
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

