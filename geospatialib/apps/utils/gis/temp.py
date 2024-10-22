def get_wms_metadata(user, dataset, reference_url):
    # try:
    #     wms = WebMapService(reference_url.path)
    # except Exception as e:
    #     raise ValueError(f'Failed to initialize WMS: {e}')
    
    # id_vars = vars_to_dict(wms.identification)
    # layer_vars = vars_to_dict(wms.contents.get(dataset.name, {}))
    # # provider_vars = vars_to_dict(wms.provider)

    if dataset.title in [None, '']:
        dataset.title = [value for value in [vars.get('title', '') 
            for vars in [layer_vars, id_vars]] 
            if isinstance(value, str) and value != ''][0]

    add_abstract = '<br><br>'.join([value for value in [vars.get('abstract', '') 
        for vars in [id_vars, layer_vars]] 
        if isinstance(value, str) and value != '' and value not in dataset.abstract])
    if add_abstract.strip() != '':
        prefix = f'<i>Retrieved from <a href="{reference_url.path}" target="_blank">{reference_url.domain}</a></i>'
        add_abstract = f'{prefix}<br><br>{add_abstract}'
        dataset.abstract = '<br><br><br>'.join([abstract for abstract in [dataset.abstract, add_abstract] if abstract != ''])


    # for field_name, var in {'bbox':'boundingBox', 'bbox_wgs84':'boundingBoxWGS84'}.items():
    #     if hasattr(dataset, field_name) and getattr(dataset, field_name) in ['', None]:
    #         w,s,e,n,*srid = layer_vars.get(var, (-180, -90, 180, 90, 'EPSG:4326'))
    #         srid = int(srid[0].split(':')[1]) if len(srid) != 0 and ':' in srid[0] else 4326
    #         corners = [(w,s), (e,s), (e,n), (w,n), (w,s)]
    #         setattr(dataset, field_name, Polygon(corners, srid=srid))
    
    if dataset.pk:
        constraints = id_vars.get('accessconstraints', '')
        if constraints and isinstance(constraints, str) and constraints.lower() not in ['', 'none']:
            attribution_instance = get_or_create_attribution(
                user,
                constraints,
                reference_url,
                raise_error=False
            )[0]
            if attribution_instance:
                dataset.attributions.add(attribution_instance)

        for name, attrs in layer_vars.get('styles', {}).items():
            legend_url = attrs.get('legend', '')
            legend_url_instance, created = get_or_create_url(
                added_by=user,
                path = legend_url,
                raise_error=False
            )
            if legend_url_instance:
                style_instance, created = get_or_create_dataset_style(
                    added_by=user,
                    dataset=dataset,
                    url=legend_url_instance,
                    raise_error=False,
                )
                if style_instance:
                    style_instance.name = name
                    style_instance.title = attrs.get('title', None)
                    style_instance.format = attrs.get('format', None)
                    style_instance.save()

        multiurl_fields = {
            'download_links': nonempty_list(layer_vars.get('dataUrls',[]), {})[0].get('url', ''),
        }
        for field_name, url in multiurl_fields.items():
            if url != '':
                url_instance = get_or_create_url(user, url, raise_error=False)[0]
                if url_instance:
                    getattr(dataset, field_name).add(url_instance)

        kw_pks = set()
        for keyword in list(set(id_vars.get('keywords', []) + layer_vars.get('keywords', []))):
            keyword_instance = get_or_create_keyword(user, keyword, raise_error=False)[0]
            if keyword_instance:
                kw_pks.add(keyword_instance.pk)
        dataset.keywords.set(kw_pks)

        # srids = set()
        # for crs in layer_vars.get('crsOptions', []):
        #     try:
        #         srid = int(crs.split(':')[-1])
        #         srids.add(srid)
        #     except:
        #         pass
        # srs_pks = SpatialRefSys.objects.filter(srid__in=list(srids)).values_list('pk', flat=True)
        # dataset.crs_options.set(srs_pks)

        dataset.reference_urls.add(reference_url)
    
    dataset.save()