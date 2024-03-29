package com.comp6239.Admin;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import com.comp6239.Admin.AdminSubjectListFragment.OnListFragmentInteractionListener;
import com.comp6239.Backend.Model.Subject;
import com.comp6239.R;

import java.util.List;

/**
 * {@link RecyclerView.Adapter} that can display a {@link Subject} and makes a call to the
 * specified {@link OnListFragmentInteractionListener}.
 * TODO: Replace the implementation with code for your data type.
 */
public class AdminMySubjectRecyclerViewAdapter extends RecyclerView.Adapter<AdminMySubjectRecyclerViewAdapter.ViewHolder> {

    private final List<Subject> mValues;
    private final OnListFragmentInteractionListener mListener;

    public AdminMySubjectRecyclerViewAdapter(List<Subject> items, OnListFragmentInteractionListener listener) {
        mValues = items;
        mListener = listener;
    }

    @Override
    public ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.fragment_subject, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(final ViewHolder holder, int position) {
        holder.mItem = mValues.get(position);
        holder.mSubjectIDView.setText(mValues.get(position).getId().toString());
        holder.mSubjectNameView.setText(mValues.get(position).getName());

        holder.mView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (null != mListener) {
                    // Notify the active callbacks interface (the activity, if the
                    // fragment is attached to one) that an item has been selected.
                    mListener.onSubjectListFragmentInteraction(holder.mItem);
                }
            }
        });
    }

    @Override
    public int getItemCount() {
        return mValues.size();
    }

    public class ViewHolder extends RecyclerView.ViewHolder {
        public final View mView;
        public final TextView mSubjectNameView;
        public final TextView mSubjectIDView;
        public Subject mItem;

        public ViewHolder(View view) {
            super(view);
            mView = view;
            mSubjectNameView = (TextView) view.findViewById(R.id.recipient_name);
            mSubjectIDView = (TextView) view.findViewById(R.id.most_recent_message);
        }

        @Override
        public String toString() {
            return super.toString() + " '" + mSubjectIDView.getText() + "'";
        }
    }
}
