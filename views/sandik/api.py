from flask import jsonify

from views.sandik.auxiliary import share_choices


def api_shares_of_member(member_id):
    shares = share_choices(member_id)
    shares_list = []
    for share in shares:
        shares_list.append({'id': share[0], 'share': share[1]})
    return jsonify({'shares': shares_list})
