from flask import Flask, render_template, request
import rdflib

app = Flask(__name__, template_folder='templates')

graph = rdflib.Graph()
graph.parse("plants-identifier.rdf", format="xml")

namespaces = {"plant": "http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#"}


def get_all_plants():
    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT ?plant ?plantName
        WHERE {
            ?plant a plant:Растение ;
                   plant:названиеРастения ?plantName .
        }
        ORDER BY ASC(?plantName)
        """,
        initNs=namespaces
    )

    plants = []
    for row in qres:
        plant_uri = row["plant"]
        plant_name = str(row["plantName"])
        plants.append({
            "uri": str(plant_uri),
            "name": plant_name
        })
    return plants


def get_plant_details(plant_uri):
    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT ?plantName ?vegSign ?genSign ?addInfo
        WHERE {
            ?plant a plant:Растение ;
                   plant:названиеРастения ?plantName .
            OPTIONAL { ?plant plant:имеетВегетативныйПризнак ?vegSign . }
            OPTIONAL { ?plant plant:имеетГенеративныйПризнак ?genSign . }
            OPTIONAL { ?plant plant:имеетДополнительныеСведения ?addInfo . }
            FILTER (?plant = <""" + plant_uri + """>)
        }
        """,
        initNs=namespaces
    )

    plant_data = {}
    for row in qres:
        plant_data = {
            "name": str(row["plantName"]),
            "vegSign": str(row["vegSign"]) if row["vegSign"] else None,
            "genSign": str(row["genSign"]) if row["genSign"] else None,
            "addInfo": str(row["addInfo"]) if row["addInfo"] else None
        }
        break

    if plant_data.get("vegSign"):
        plant_data.update(get_vegetative_details(plant_data["vegSign"]))

    if plant_data.get("genSign"):
        plant_data.update(get_generative_details(plant_data["genSign"]))

    if plant_data.get("addInfo"):
        plant_data.update(get_additional_info(plant_data["addInfo"]))

    return plant_data


def get_vegetative_details(veg_sign_uri):
    details = {}

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT ?root ?rootType ?rootMod
        WHERE {
            ?vegSign plant:ВегетативныйПризнакВключаетКорень ?root .
            ?root plant:типКорня ?rootType .
            OPTIONAL { ?root plant:модификацияКорня ?rootMod . }
            FILTER (?vegSign = <""" + veg_sign_uri + """>)
        }
        """,
        initNs=namespaces
    )

    for row in qres:
        details["root_type"] = str(row["rootType"])
        details["root_modification"] = str(row["rootMod"]) if row["rootMod"] else "Отсутствует"

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT ?leaf ?leafForm ?leafEdge ?leafVenation ?leafArrangement ?leafComplexity
        WHERE {
            ?vegSign plant:ВегетативныйПризнакВключаетЛист ?leaf .
            ?leaf plant:формаЛиста ?leafForm ;
                  plant:крайЛиста ?leafEdge ;
                  plant:жилкованиеЛиста ?leafVenation ;
                  plant:расположениеЛиста ?leafArrangement ;
                  plant:сложностьЛиста ?leafComplexity .
            FILTER (?vegSign = <""" + veg_sign_uri + """>)
        }
        """,
        initNs=namespaces
    )

    for row in qres:
        details["leaf_form"] = str(row["leafForm"])
        details["leaf_edge"] = str(row["leafEdge"])
        details["leaf_venation"] = str(row["leafVenation"])
        details["leaf_arrangement"] = str(row["leafArrangement"])
        details["leaf_complexity"] = str(row["leafComplexity"])

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT ?stem ?stemForm ?stemBranching ?stemPubescence ?stemGrowthType
        WHERE {
            ?vegSign plant:ВегетативныйПризнакВключаетСтебель ?stem .
            ?stem plant:формаСтебля ?stemForm ;
                  plant:разветвлённостьСтебля ?stemBranching ;
                  plant:опушениеСтебля ?stemPubescence ;
                  plant:типРостаСтебля ?stemGrowthType .
            FILTER (?vegSign = <""" + veg_sign_uri + """>)
        }
        """,
        initNs=namespaces
    )

    for row in qres:
        details["stem_form"] = str(row["stemForm"])
        details["stem_branching"] = str(row["stemBranching"])
        details["stem_pubescence"] = str(row["stemPubescence"])
        details["stem_growth_type"] = str(row["stemGrowthType"])

    return details


def get_generative_details(gen_sign_uri):
    details = {}

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT ?flower ?flowerSymmetry ?flowerOvary ?flowerInflorescence ?flowerParts
        WHERE {
            ?genSign plant:ГенеративныйПризнакВключаетЦветок ?flower .
            ?flower plant:симметрияЦветка ?flowerSymmetry ;
                    plant:типЗавязиЦветка ?flowerOvary ;
                    plant:типСоцветияЦветка ?flowerInflorescence ;
                    plant:числоЧастейЦветка ?flowerParts .
            FILTER (?genSign = <""" + gen_sign_uri + """>)
        }
        """,
        initNs=namespaces
    )

    for row in qres:
        details["flower_symmetry"] = str(row["flowerSymmetry"])
        details["flower_ovary"] = str(row["flowerOvary"])
        details["flower_inflorescence"] = str(row["flowerInflorescence"])
        details["flower_parts"] = float(row["flowerParts"])

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT ?fruit ?fruitType
        WHERE {
            ?genSign plant:ГенеративныйПризнакВключаетПлод ?fruit .
            ?fruit plant:типПлода ?fruitType .
            FILTER (?genSign = <""" + gen_sign_uri + """>)
        }
        """,
        initNs=namespaces
    )

    for row in qres:
        details["fruit_type"] = str(row["fruitType"])

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT ?seed ?seedForm ?seedSize ?seedEndosperm
        WHERE {
            ?genSign plant:ГенеративныйПризнакВключаетСемя ?seed .
            ?seed plant:формаСемени ?seedForm ;
                  plant:размерСемени ?seedSize ;
                  plant:наличиеЭндоспермаСемени ?seedEndosperm .
            FILTER (?genSign = <""" + gen_sign_uri + """>)
        }
        """,
        initNs=namespaces
    )

    for row in qres:
        details["seed_form"] = str(row["seedForm"])
        details["seed_size"] = str(row["seedSize"])
        details["seed_endosperm"] = bool(row["seedEndosperm"])

    return details


def get_additional_info(add_info_uri):
    details = {}

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT ?distribution ?ecology ?habitat ?bloomPeriod
        WHERE {
            ?addInfo plant:Распространение ?distribution ;
                     plant:ЭкологическаяХарактеристика ?ecology ;
                     plant:средаОбитания ?habitat ;
                     plant:периодЦветения ?bloomPeriod .
            FILTER (?addInfo = <""" + add_info_uri + """>)
        }
        """,
        initNs=namespaces
    )

    for row in qres:
        details["distribution"] = str(row["distribution"])
        details["ecology"] = str(row["ecology"])
        details["habitat"] = str(row["habitat"])
        details["bloom_period"] = str(row["bloomPeriod"])

    return details


def search_plants(**filters):
    query_parts = [
        "PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>",
        "SELECT DISTINCT ?plant ?plantName",
        "WHERE {",
        "    ?plant a plant:Растение ;",
        "           plant:названиеРастения ?plantName ."
    ]

    conditions = []

    # Вегетативные признаки
    if filters.get('leaf_form'):
        query_parts.extend([
            "    ?plant plant:имеетВегетативныйПризнак ?vegSign .",
            "    ?vegSign plant:ВегетативныйПризнакВключаетЛист ?leaf .",
            "    ?leaf plant:формаЛиста ?leafForm ."
        ])
        conditions.append(f'?leafForm = "{filters["leaf_form"]}"')

    if filters.get('leaf_edge'):
        query_parts.extend([
            "    ?plant plant:имеетВегетативныйПризнак ?vegSign .",
            "    ?vegSign plant:ВегетативныйПризнакВключаетЛист ?leaf .",
            "    ?leaf plant:крайЛиста ?leafEdge ."
        ])
        conditions.append(f'?leafEdge = "{filters["leaf_edge"]}"')

    if filters.get('leaf_venation'):
        query_parts.extend([
            "    ?plant plant:имеетВегетативныйПризнак ?vegSign .",
            "    ?vegSign plant:ВегетативныйПризнакВключаетЛист ?leaf .",
            "    ?leaf plant:жилкованиеЛиста ?leafVenation ."
        ])
        conditions.append(f'?leafVenation = "{filters["leaf_venation"]}"')

    if filters.get('leaf_arrangement'):
        query_parts.extend([
            "    ?plant plant:имеетВегетативныйПризнак ?vegSign .",
            "    ?vegSign plant:ВегетативныйПризнакВключаетЛист ?leaf .",
            "    ?leaf plant:расположениеЛиста ?leafArrangement ."
        ])
        conditions.append(f'?leafArrangement = "{filters["leaf_arrangement"]}"')

    if filters.get('leaf_complexity'):
        query_parts.extend([
            "    ?plant plant:имеетВегетативныйПризнак ?vegSign .",
            "    ?vegSign plant:ВегетативныйПризнакВключаетЛист ?leaf .",
            "    ?leaf plant:сложностьЛиста ?leafComplexity ."
        ])
        conditions.append(f'?leafComplexity = "{filters["leaf_complexity"]}"')

    if filters.get('root_type'):
        query_parts.extend([
            "    ?plant plant:имеетВегетативныйПризнак ?vegSign .",
            "    ?vegSign plant:ВегетативныйПризнакВключаетКорень ?root .",
            "    ?root plant:типКорня ?rootType ."
        ])
        conditions.append(f'?rootType = "{filters["root_type"]}"')

    if filters.get('stem_growth_type'):
        query_parts.extend([
            "    ?plant plant:имеетВегетативныйПризнак ?vegSign .",
            "    ?vegSign plant:ВегетативныйПризнакВключаетСтебель ?stem .",
            "    ?stem plant:типРостаСтебля ?stemGrowthType ."
        ])
        conditions.append(f'?stemGrowthType = "{filters["stem_growth_type"]}"')

    if filters.get('stem_branching'):
        query_parts.extend([
            "    ?plant plant:имеетВегетативныйПризнак ?vegSign .",
            "    ?vegSign plant:ВегетативныйПризнакВключаетСтебель ?stem .",
            "    ?stem plant:разветвлённостьСтебля ?stemBranching ."
        ])
        conditions.append(f'?stemBranching = "{filters["stem_branching"]}"')

    # Генеративные признаки
    if filters.get('fruit_type'):
        query_parts.extend([
            "    ?plant plant:имеетГенеративныйПризнак ?genSign .",
            "    ?genSign plant:ГенеративныйПризнакВключаетПлод ?fruit .",
            "    ?fruit plant:типПлода ?fruitType ."
        ])
        conditions.append(f'?fruitType = "{filters["fruit_type"]}"')

    if filters.get('flower_symmetry'):
        query_parts.extend([
            "    ?plant plant:имеетГенеративныйПризнак ?genSign .",
            "    ?genSign plant:ГенеративныйПризнакВключаетЦветок ?flower .",
            "    ?flower plant:симметрияЦветка ?flowerSymmetry ."
        ])
        conditions.append(f'?flowerSymmetry = "{filters["flower_symmetry"]}"')

    if filters.get('flower_inflorescence'):
        query_parts.extend([
            "    ?plant plant:имеетГенеративныйПризнак ?genSign .",
            "    ?genSign plant:ГенеративныйПризнакВключаетЦветок ?flower .",
            "    ?flower plant:типСоцветияЦветка ?flowerInflorescence ."
        ])
        conditions.append(f'?flowerInflorescence = "{filters["flower_inflorescence"]}"')

    if filters.get('seed_size'):
        query_parts.extend([
            "    ?plant plant:имеетГенеративныйПризнак ?genSign .",
            "    ?genSign plant:ГенеративныйПризнакВключаетСемя ?seed .",
            "    ?seed plant:размерСемени ?seedSize ."
        ])
        conditions.append(f'?seedSize = "{filters["seed_size"]}"')

    # Дополнительные сведения
    if filters.get('habitat'):
        query_parts.extend([
            "    ?plant plant:имеетДополнительныеСведения ?addInfo .",
            "    ?addInfo plant:средаОбитания ?habitat ."
        ])
        conditions.append(f'?habitat = "{filters["habitat"]}"')

    if filters.get('bloom_period'):
        query_parts.extend([
            "    ?plant plant:имеетДополнительныеСведения ?addInfo .",
            "    ?addInfo plant:периодЦветения ?bloomPeriod ."
        ])
        conditions.append(f'?bloomPeriod = "{filters["bloom_period"]}"')

    if filters.get('distribution'):
        query_parts.extend([
            "    ?plant plant:имеетДополнительныеСведения ?addInfo .",
            "    ?addInfo plant:Распространение ?distribution ."
        ])
        conditions.append(f'?distribution = "{filters["distribution"]}"')

    if conditions:
        query_parts.append("    FILTER (" + " && ".join(conditions) + ")")

    query_parts.extend([
        "}",
        "ORDER BY ASC(?plantName)"
    ])

    final_query = "\n".join(query_parts)

    try:
        qres = graph.query(final_query, initNs=namespaces)

        plants = []
        for row in qres:
            plants.append({
                "uri": str(row["plant"]),
                "name": str(row["plantName"])
            })

        return plants
    except Exception as e:
        print(f"Query error: {e}")
        return []


def get_search_options():
    """Получает возможные варианты для поисковых фильтров"""
    options = {}

    # Вегетативные признаки
    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT DISTINCT ?leafForm
        WHERE {
            ?leaf a plant:Лист ;
                  plant:формаЛиста ?leafForm .
        }
        ORDER BY ASC(?leafForm)
        """,
        initNs=namespaces
    )
    options['leaf_forms'] = [str(row["leafForm"]) for row in qres]

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT DISTINCT ?leafEdge
        WHERE {
            ?leaf a plant:Лист ;
                  plant:крайЛиста ?leafEdge .
        }
        ORDER BY ASC(?leafEdge)
        """,
        initNs=namespaces
    )
    options['leaf_edges'] = [str(row["leafEdge"]) for row in qres]

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT DISTINCT ?leafVenation
        WHERE {
            ?leaf a plant:Лист ;
                  plant:жилкованиеЛиста ?leafVenation .
        }
        ORDER BY ASC(?leafVenation)
        """,
        initNs=namespaces
    )
    options['leaf_venations'] = [str(row["leafVenation"]) for row in qres]

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT DISTINCT ?leafArrangement
        WHERE {
            ?leaf a plant:Лист ;
                  plant:расположениеЛиста ?leafArrangement .
        }
        ORDER BY ASC(?leafArrangement)
        """,
        initNs=namespaces
    )
    options['leaf_arrangements'] = [str(row["leafArrangement"]) for row in qres]

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT DISTINCT ?leafComplexity
        WHERE {
            ?leaf a plant:Лист ;
                  plant:сложностьЛиста ?leafComplexity .
        }
        ORDER BY ASC(?leafComplexity)
        """,
        initNs=namespaces
    )
    options['leaf_complexities'] = [str(row["leafComplexity"]) for row in qres]

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT DISTINCT ?rootType
        WHERE {
            ?root a plant:Корень ;
                  plant:типКорня ?rootType .
        }
        ORDER BY ASC(?rootType)
        """,
        initNs=namespaces
    )
    options['root_types'] = [str(row["rootType"]) for row in qres]

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT DISTINCT ?growthType
        WHERE {
            ?stem a plant:Стебель ;
                  plant:типРостаСтебля ?growthType .
        }
        ORDER BY ASC(?growthType)
        """,
        initNs=namespaces
    )
    options['stem_growth_types'] = [str(row["growthType"]) for row in qres]

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT DISTINCT ?stemBranching
        WHERE {
            ?stem a plant:Стебель ;
                  plant:разветвлённостьСтебля ?stemBranching .
        }
        ORDER BY ASC(?stemBranching)
        """,
        initNs=namespaces
    )
    options['stem_branchings'] = [str(row["stemBranching"]) for row in qres]

    # Генеративные признаки
    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT DISTINCT ?fruitType
        WHERE {
            ?fruit a plant:Плод ;
                   plant:типПлода ?fruitType .
        }
        ORDER BY ASC(?fruitType)
        """,
        initNs=namespaces
    )
    options['fruit_types'] = [str(row["fruitType"]) for row in qres]

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT DISTINCT ?flowerSymmetry
        WHERE {
            ?flower a plant:Цветок ;
                    plant:симметрияЦветка ?flowerSymmetry .
        }
        ORDER BY ASC(?flowerSymmetry)
        """,
        initNs=namespaces
    )
    options['flower_symmetries'] = [str(row["flowerSymmetry"]) for row in qres]

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT DISTINCT ?flowerInflorescence
        WHERE {
            ?flower a plant:Цветок ;
                    plant:типСоцветияЦветка ?flowerInflorescence .
        }
        ORDER BY ASC(?flowerInflorescence)
        """,
        initNs=namespaces
    )
    options['flower_inflorescences'] = [str(row["flowerInflorescence"]) for row in qres]

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT DISTINCT ?seedSize
        WHERE {
            ?seed a plant:Семя ;
                  plant:размерСемени ?seedSize .
        }
        ORDER BY ASC(?seedSize)
        """,
        initNs=namespaces
    )
    options['seed_sizes'] = [str(row["seedSize"]) for row in qres]

    # Дополнительные сведения
    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT DISTINCT ?habitat
        WHERE {
            ?addInfo a plant:ДополнительныеСведения ;
                     plant:средаОбитания ?habitat .
        }
        ORDER BY ASC(?habitat)
        """,
        initNs=namespaces
    )
    options['habitats'] = [str(row["habitat"]) for row in qres]

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT DISTINCT ?bloomPeriod
        WHERE {
            ?addInfo a plant:ДополнительныеСведения ;
                     plant:периодЦветения ?bloomPeriod .
        }
        ORDER BY ASC(?bloomPeriod)
        """,
        initNs=namespaces
    )
    options['bloom_periods'] = [str(row["bloomPeriod"]) for row in qres]

    qres = graph.query(
        """
        PREFIX plant: <http://www.semanticweb.org/christina/ontologies/2025/10/plant-identifier#>
        SELECT DISTINCT ?distribution
        WHERE {
            ?addInfo a plant:ДополнительныеСведения ;
                     plant:Распространение ?distribution .
        }
        ORDER BY ASC(?distribution)
        """,
        initNs=namespaces
    )
    options['distributions'] = [str(row["distribution"]) for row in qres]

    return options


@app.route('/')
def index():
    search_options = get_search_options()
    return render_template('index.html', search_options=search_options)


@app.route('/plants')
def display_plants():
    plants = get_all_plants()
    return render_template('plants.html', plants=plants)


@app.route('/plant/<path:plant_uri>')
def plant_details(plant_uri):
    plant_uri = plant_uri.replace(' ', '%20')
    plant_data = get_plant_details(plant_uri)
    return render_template('plant_details.html', plant=plant_data)


@app.route('/search', methods=['POST'])
def search():
    # Вегетативные признаки
    leaf_form = request.form.get('leaf_form')
    leaf_edge = request.form.get('leaf_edge')
    leaf_venation = request.form.get('leaf_venation')
    leaf_arrangement = request.form.get('leaf_arrangement')
    leaf_complexity = request.form.get('leaf_complexity')
    root_type = request.form.get('root_type')
    stem_growth_type = request.form.get('stem_growth_type')
    stem_branching = request.form.get('stem_branching')

    # Генеративные признаки
    fruit_type = request.form.get('fruit_type')
    flower_symmetry = request.form.get('flower_symmetry')
    flower_inflorescence = request.form.get('flower_inflorescence')
    seed_size = request.form.get('seed_size')

    # Дополнительные сведения
    habitat = request.form.get('habitat')
    bloom_period = request.form.get('bloom_period')
    distribution = request.form.get('distribution')

    filters = {}
    if leaf_form: filters['leaf_form'] = leaf_form
    if leaf_edge: filters['leaf_edge'] = leaf_edge
    if leaf_venation: filters['leaf_venation'] = leaf_venation
    if leaf_arrangement: filters['leaf_arrangement'] = leaf_arrangement
    if leaf_complexity: filters['leaf_complexity'] = leaf_complexity
    if root_type: filters['root_type'] = root_type
    if stem_growth_type: filters['stem_growth_type'] = stem_growth_type
    if stem_branching: filters['stem_branching'] = stem_branching
    if fruit_type: filters['fruit_type'] = fruit_type
    if flower_symmetry: filters['flower_symmetry'] = flower_symmetry
    if flower_inflorescence: filters['flower_inflorescence'] = flower_inflorescence
    if seed_size: filters['seed_size'] = seed_size
    if habitat: filters['habitat'] = habitat
    if bloom_period: filters['bloom_period'] = bloom_period
    if distribution: filters['distribution'] = distribution

    plants = search_plants(**filters)
    search_options = get_search_options()

    return render_template('search_results.html',
                           plants=plants,
                           filters=filters,
                           search_options=search_options)


if __name__ == '__main__':
    app.run(debug=True)