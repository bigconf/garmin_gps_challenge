import folium

def generate_map_with_stats(gdf, tooltip_field, alias, crossed, uncrossed, crossedpct, output_path="postcode_map_with_stats.html"):
    def style_function(feature):
        crossed_flag = feature['properties'].get('crossed', False)
        return {
            'fillColor': 'green' if crossed_flag else 'red',
            'color': 'black',
            'weight': 0.7,
            'fillOpacity': 0.2,
        }

    m = folium.Map(location=[52.1, 5.1], zoom_start=6)

    folium.GeoJson(
        gdf,
        name='Postcode Areas',
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=[tooltip_field], aliases=[alias])
    ).add_to(m)

    stats_html = f"""
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 300px; height: 120px; 
                background-color: white; z-index:9999; font-size:14px;
                border:2px solid grey; padding: 10px;">
        <b>Postcode Challenge Stats</b><br>
        Crossed: {crossed}<br>
        Remaining: {uncrossed}<br>
        Completed: {crossedpct:.1f}%
    </div>
    """
    m.get_root().html.add_child(folium.Element(stats_html))
    folium.LayerControl().add_to(m)
    m.save(output_path)
    return output_path
