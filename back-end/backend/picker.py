import random
import datetime
from flask import Blueprint, render_template, request, redirect, url_for
from backend import configs
from etl import models
from cachetools import LFUCache

models.create_db_connection(configs)
bp = Blueprint("picker", __name__)

top_banners = LFUCache(maxsize=100)
users_history = LFUCache(maxsize=1000)


@bp.route("/pick", methods=['GET', 'POST'])
def pick_banner():
    if request.method == 'GET':
        return render_template('show_banner.html')
    else:
        username = request.values['username']
        campaign_id = request.values['campaign_id']
        return redirect(url_for('picker.show_banner', username=username, campaign_id=campaign_id))


@bp.route("/pick/<int:campaign_id>/<string:username>", methods=['GET'])
def show_banner(campaign_id, username):
    data_revision = models.get_data_revision()
    if (campaign_id not in top_banners) or (top_banners[campaign_id]['revision'] != data_revision):
        update_campaign(quarter=int(datetime.datetime.now().minute/15), campaign_id=campaign_id, data_revision=data_revision)
    last_seen = -1
    if username in users_history:
        last_seen = users_history[username]

    if campaign_id not in top_banners:
        return redirect(url_for('picker.pick_banner'))

    tops = top_banners[campaign_id]['banners']
    random.shuffle(tops)
    banner = tops[0]
    if banner == last_seen and len(tops) > 1:
        banner = tops[1]
    users_history[username] = banner
    image_path = 'images/image_{}.jpeg'.format(banner)
    return render_template('show_banner.html', image_path=image_path)


def update_campaign(quarter, campaign_id, data_revision):
    tops_by_revenue = models.get_tops_by_revenue(quarter=quarter, campaign_id=campaign_id)
    tops_by_clicks = models.get_tops_by_revenue(quarter=quarter, campaign_id=campaign_id)
    tops_by_random = models.get_tops_by_random(quarter=quarter, campaign_id=campaign_id)
    for banner in tops_by_clicks:
        if len(tops_by_revenue) < 5 and banner not in tops_by_revenue:
            tops_by_revenue.append(banner)
    for banner in tops_by_random:
        if len(tops_by_revenue) < 5 and banner not in tops_by_revenue:
            tops_by_revenue.append(banner)
    if len(tops_by_revenue) > 0:
        top_banners[campaign_id] = {'banners': [], 'revision': 0}
        top_banners[campaign_id]['banners'] = tops_by_revenue
        top_banners[campaign_id]['revision'] = data_revision
